import os, sys, time
import pickle
import pprint
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import rcParams
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import ImageGrid

from analysis.lib.fitting import fit
from analysis import config

# import entanglement_analysis as ea

### configure stuff
config.outputdir = r'/Users/wp/Documents/TUD/LDE/analysis/output'

rcParams['mathtext.default'] = 'regular'
rcParams['legend.numpoints'] = 1
rcParams['legend.frameon'] = False

fidspacing = 1 # if n, then every n-th datapoint from the fidelity data is used

### tools
def idx(arr, val):
    return argmin(abs(arr-val))

### get the data
prjfidsrcdir = os.path.join(config.outputdir, '20121026-tpqi')
fidsrcdir = os.path.join(config.outputdir, '20121102-ldefidelity')
savedir = os.path.join(config.outputdir, time.strftime('%Y%m%d')+'-ldefidelity')

apsrcdir = os.path.join(config.outputdir, '20121101-afterpulsing')

fid = {}
f = np.load(os.path.join(fidsrcdir, 'fidelities.npz'))
for k in f.keys():
    fid[k] = f[k]
f.close()

prjfid = {}
f = np.load(os.path.join(prjfidsrcdir, 'fidelities.npz'))
for k in f.keys():
    prjfid[k] = f[k]
f.close()


psi1mindtidx = idx(fid['dtvals'], 20)
psi1maxdtidx = idx(fid['dtvals'], 150)
psi1winidx = idx(fid['winvals'], 150)
psi1ch0idx = idx(fid['ch0starts'], 639)
psi1ch1idx = idx(fid['ch1starts'], 668)
psi1cut = fid['psi1fids'][psi1mindtidx:psi1maxdtidx:fidspacing, psi1winidx, psi1ch0idx, psi1ch1idx]
u_psi1cut = fid['u_psi1fids'][psi1mindtidx:psi1maxdtidx:fidspacing, psi1winidx, psi1ch0idx, psi1ch1idx]
psi1x = fid['dtvals'][psi1mindtidx:psi1maxdtidx:fidspacing]

psi2mindtidx = idx(fid['dtvals'], 40)
psi2maxdtidx = idx(fid['dtvals'], 150)
psi2winidx = idx(fid['winvals'], 150)
psi2ch0idx = idx(fid['ch0starts'], 639)
psi2ch1idx = idx(fid['ch1starts'], 668)
psi2cut = fid['psi2fids'][psi2mindtidx:psi2maxdtidx:fidspacing, psi2winidx, psi2ch0idx, psi2ch1idx]
u_psi2cut = fid['u_psi2fids'][psi2mindtidx:psi2maxdtidx:fidspacing, psi2winidx, psi2ch0idx, psi2ch1idx]
psi2x = fid['dtvals'][psi2mindtidx:psi2maxdtidx:fidspacing]

### 1st order correction of expected fidelities

# afterpulsing ratio
apf = np.load(os.path.join(apsrcdir, 'afterpulsing_vs_nvcounts.npz'))
aptvals = apf['tvals']
apratios = apf['ratios']
u_apratios = apf['u_ratios']
apf.close()

apidx = idx(aptvals, 150)
p_afterpulsing = apratios[apidx]
u_p_afterpulsing = u_apratios[apidx]

# general p for a mixed state
corrf = np.load(os.path.join(fidsrcdir, 'correlations.npz'))
_psi2 = corrf['correctedpsi2correlations']
_u_psi2 = corrf['u_correctedpsi2correlations']
corrf.close()

_dts = np.array([idx(fid['dtvals'], dt) for dt in prjfid['dts']])
psi2_ZZ_for_psi1 = _psi2[_dts,psi1winidx,psi2ch0idx,psi2ch1idx,0,:]
u_psi2_ZZ_for_psi1 = _u_psi2[_dts,psi1winidx,psi2ch0idx,psi2ch1idx,0,:]
p_mixed_for_psi1 = 2*(psi2_ZZ_for_psi1[...,0] + psi2_ZZ_for_psi1[...,3])
u_p_mixed_for_psi1 = np.sqrt(2) * np.sqrt(u_psi2_ZZ_for_psi1[...,0]**2 + u_psi2_ZZ_for_psi1[...,3]**2)

psi2_ZZ_for_psi2 = _psi2[_dts,psi2winidx,psi2ch0idx,psi2ch1idx,0,:]
u_psi2_ZZ_for_psi2 = _u_psi2[_dts,psi2winidx,psi2ch0idx,psi2ch1idx,0,:]
p_mixed_for_psi2 = 2*(psi2_ZZ_for_psi2[...,0] + psi2_ZZ_for_psi2[...,3])
u_p_mixed_for_psi2 = np.sqrt(2) * np.sqrt(u_psi2_ZZ_for_psi2[...,0]**2 + u_psi2_ZZ_for_psi2[...,3]**2)



# expected fidelities
psi1expected = 0.25*p_mixed_for_psi1 + 0.25*p_afterpulsing + \
        (1. - p_mixed_for_psi1 - p_afterpulsing) * prjfid['fid']
u_psi1expected = ( ((0.25-prjfid['fid'])*u_p_afterpulsing)**2 + \
        ((0.25-prjfid['fid'])*u_p_mixed_for_psi1)**2 + \
        ((1-p_mixed_for_psi1-p_afterpulsing)*prjfid['u_fid'])**2 )**0.5

psi2expected = 0.25 * (p_mixed_for_psi2) + (1. - p_mixed_for_psi2) * prjfid['fid']
u_psi2expected = (((0.25-prjfid['fid'])*u_p_mixed_for_psi2)**2 + \
        ((1-p_mixed_for_psi2)*prjfid['u_fid'])**2 )**0.5

### plot
fig,(ax1,ax2) = plt.subplots(1,2, figsize=(12,6), sharey=True, sharex=True)

### psi1
ax1.errorbar(prjfid['dts'], prjfid['fid'], 
    yerr=prjfid['u_fid'], fmt='o',
    color='0.5',
    label='TPQI')

ax1.errorbar(prjfid['dts'], psi1expected, 
    yerr=u_psi1expected, fmt='ko',
    label='corrected')

ax1.errorbar(psi1x, psi1cut, 
    yerr=u_psi1cut, fmt='ro',
    label='measured')

ax1.legend()
ax1.set_title('Psi1')
ax1.set_xlabel('dt (bins)')
ax1.set_ylabel('fidelity')
ax1.set_ylim(0.5,0.9)
ax1.set_xlim(0,120)


### psi2
ax2.errorbar(prjfid['dts'], prjfid['fid'], 
    yerr=prjfid['u_fid'], fmt='o',
    color='0.5',
    label='TPQI expectation')

ax2.errorbar(prjfid['dts'], psi2expected, 
    yerr=u_psi2expected, fmt='ko',
    label='corrected expectation')

ax2.errorbar(psi2x, psi2cut, 
    yerr=u_psi2cut, fmt='ro',
    label='measured')

ax2.set_title('Psi2')
ax2.set_xlabel('dt (bins)')
