import os, sys
import numpy as np
import h5py
import logging

from matplotlib import pyplot as plt
from analysis.lib.tools import plot
from analysis.lib.m2.ssro import sequence
from analysis.lib.tools import toolbox
from analysis.lib.fitting import fit,esr


def analyze_dark_esr(guess_ctr, guess_splitN,
guess_offset = 1,
guess_width = 0.27e-3,
guess_amplitude = 0.3,
min_dip_depth = 0.80, 
timestamp = None,
add_folder = None,
ret='f0',
ssro_calib_folder='',
do_save=True,
sweep_direction = 'right',
**kw):

    if timestamp != None:
        folder = toolbox.data_from_time(timestamp)
    else:
        folder = toolbox.latest_data('DarkESR')

    if add_folder !=None:
        folder = add_folder

    print folder
    a = sequence.SequenceAnalysis(folder)
    a.get_sweep_pts()
    a.get_readout_results('ssro')
    a.get_electron_ROC()

    x = a.sweep_pts # convert to MHz
    y = a.p0.reshape(-1)[:]

    # Find the most left esr resonance
    ## I added this to be more robust for SSRO calibration.Please monitor if this is better - Machiel may-2014
    ## THT: this makes the loop go haywire if there is no ESR dip (it always finds something = bad)

    j=0
    print 'j = '+str(j)
    print folder
    print y[21]
    k = len(y)
    print 'min_dip_depth = ' + str(min_dip_depth)

    

    ### Option to make the dip search sweep towards left or right, usefull in case of N polarization
    if sweep_direction == 'left':
        y1 = y[::-1]
        x1 = x[::-1]
        guess_splitN = -1*guess_splitN
    elif sweep_direction == 'right':
        y1 = y
        x1 = x

    while y1[j]>min_dip_depth and j < len(y)-2:  #y[j]>0.93*y[j+1]: # such that we account for noise
        k = j
        j += 1
    #j = len(y)-2
    if k > len(y)-3:
        print 'Could not find dip'
        return
    else:
        guess_ctr = x1[k]+ guess_splitN #convert to GHz and go to middle dip

        print 'guess_ctr= '+str(guess_ctr)
        print 'k'+str(k)
    ## I added this to be more robust for SSRO calibration.Please monitor if this is better - Machiel may-2014

    
    ### Do the fitting ###

    ### This fuction was used until 141015, but did not support differnt amplitudes, replaced by the function below - THT 141015
    # fit_result = fit.fit1d(x, y, esr.fit_ESR_gauss, guess_offset,
    #         guess_amplitude, guess_width, guess_ctr,
    #         (3, guess_splitN),
    #         do_print=True, ret=True, fixed=[])


    A_min1 = fit.Parameter(guess_amplitude, 'A_min1')
    A_plus1 = fit.Parameter(guess_amplitude, 'A_plus1')
    A_0 = fit.Parameter(guess_amplitude, 'A_0')
    o = fit.Parameter(guess_offset, 'o')
    x0 = fit.Parameter(guess_ctr, 'x0')
    sigma = fit.Parameter(guess_width, 'sigma')
    Nsplit = fit.Parameter(np.abs(guess_splitN), 'Nsplit')
    


    def fitfunc(x):
        # return o() - A_min1()*np.exp(-((x-(x0()-splitting-Nsplit()))/sigma())**2) \
        #         - A_min1()*np.exp(-((x-(x0()+splitting-Nsplit()))/sigma())**2) \
        #         - A_plus1()*np.exp(-((x-(x0()-splitting+Nsplit()))/sigma())**2) \
        #         - A_plus1()*np.exp(-((x-(x0()+splitting+Nsplit()))/sigma())**2) \
        #         - A_0()*np.exp(-((x-(x0()+Nsplit()))/sigma())**2) \
        #         - A_0()*np.exp(-((x-(x0()-Nsplit()))/sigma())**2)
        return o() - A_min1()*np.exp(-((x-(x0()-Nsplit()))/sigma())**2) \
                - A_plus1()*np.exp(-((x-(x0()+Nsplit()))/sigma())**2) \
                - A_0()*np.exp(-((x-x0())/sigma())**2) \

    fit_result = fit.fit1d(x, y, None, p0 = [A_min1, A_plus1, A_0, sigma, o, x0, Nsplit],
        fitfunc = fitfunc, do_print=True, ret=True, fixed=[])



    print 'fit finished'
    print do_save
    if do_save:
        print 'saving data and fit'
        if fit_result:
            #print 'fit result'
            #print fit_result
            
            fig, ax = plt.subplots(1,1)
            plot.plot_fit1d(fit_result, np.linspace(min(x), max(x), 1000), ax=ax, plot_data=True, **kw)
            plt.savefig(os.path.join(folder, 'darkesr_analysis.png'),
            format='png')
            plt.close(fig)
    if ret == 'f0':
        f0 = fit_result['params_dict']['x0']
        u_f0 = fit_result['error_dict']['x0']
        return f0, u_f0

def analyze_dark_esr_single( 
guess_offset = 1,
guess_width = 0.2e-3,
guess_amplitude = 0.3,
timestamp = None,
add_folder = None,
ret='f0',
ssro_calib_folder='',
do_save=True,
**kw):

    if timestamp != None:
        folder = toolbox.data_from_time(timestamp)
    else:
        folder = toolbox.latest_data('DarkESR')


    if add_folder !=None:
        folder = add_folder

    a = sequence.SequenceAnalysis(folder)
    a.get_sweep_pts()
    a.get_readout_results('ssro')
    a.get_electron_ROC()

    x = a.sweep_pts # convert to MHz
    y = a.p0.reshape(-1)[:]

    guess_ctr = x[y.argmin()]
    print 'guess_ctr = '+str(guess_ctr)
    ## I added this to be more robust for SSRO calibration.Please monitor if this is better - Machiel may-2014
    guess_offset=np.average(y)
    dip_threshold=guess_offset-1.5*np.std(y)
    print guess_offset
    print dip_threshold

    # if min(y) > dip_threshold:
    #     print 'Could not find dip'
    #     return

    fit_result = fit.fit1d(x, y, esr.fit_ESR_gauss, guess_offset,
            guess_amplitude, guess_width, guess_ctr,
            do_print=True, ret=True, fixed=[])

    if ret == 'f0':
        f0 = fit_result['params_dict']['x0']
        u_f0 = fit_result['error_dict']['x0']
        return f0, u_f0

    print do_save
    if do_save:
        print 'saving data and fit'
        if fit_result:
            #print 'fit result'
            #print fit_result
            
            fig, ax = plt.subplots(1,1)
            plot.plot_fit1d(fit_result, np.linspace(min(x), max(x), 1000), ax=ax, plot_data=True, **kw)
            plt.savefig(os.path.join(folder, 'darkesr_analysis.png'),
            format='png')
            plt.close(fig)
    if ret == 'f0':
        f0 = fit_result['params_dict']['x0']
        u_f0 = fit_result['error_dict']['x0']
        return f0, u_f0







