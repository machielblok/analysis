import os, sys
import numpy as np
import h5py
import logging

from matplotlib import pyplot as plt

from analysis.lib import fitting
from analysis.lib.m2.ssro import ssro, sequence
from analysis.lib.tools import toolbox
from analysis.lib.fitting import fit, ramsey; reload(ramsey)
from analysis.lib.tools import plot
from analysis.lib.math import error


def fit_Ramsey_3cos(timestamp = None,
	ssro_calib_folder = None,
	guess_f1 = 1,
	guess_A1 = 0.33,
	guess_phi1 = 0.,
	guess_f2 = 0,
	guess_A2 = 0.15,
	guess_phi2 = 0.,
	guess_f3 = 1, 
	guess_A3 = 0.33,
	guess_phi3 = 0.,
	guess_tau = 50000,
	guess_a = 0.5,
	fixed = []):

	"""
	Fits gaussian decaying sum of three cosines to electron Ramsey data.
	Inputs:
	- timestamp: timestamp of data. If none, takes latest data that contains 'ElectronRamsey'
	- ssro_calib_folder: folder of SSRO calibration file
	- guess_f1: initial guess for  frequency of first cosine
	- guess_A1: initial guess for amplitude of first cosine
	- guess_phi1: initial guess for amplitude of first cosine
	- Same parameters for cosine 2 and cosine 3
	- guess_tau: guess for T2*
	- guess_a: guess for offset
	- fixed: fixes fitting parameters with initial guess according to [tau, guess_a, f1, A1, phi1, f2, A2, phi2, f3, A3, phi3]

	Good initial guesses for the frequencies are:
	f1: detuning + N_HF_splt
	f2: 0,
	f3: detuning + N_HF_splt
	"""

	### script
	if timestamp != None:
	    folder = toolbox.data_from_time(timestamp)
	else:
	    folder = toolbox.latest_data('ElectronRamsey')

	a = sequence.SequenceAnalysis(folder)
	a.get_sweep_pts()
	a.get_readout_results(name='ssro')
	if ssro_calib_folder != None:
		a.get_electron_ROC(ssro_calib_folder = ssro_calib_folder)
	else: 
		a.get_electron_ROC()

	# Plot data
	ax = a.plot_result_vs_sweepparam(ret='ax', name='ssro')

	p0, fitfunc_0, fitfunc_str_0 = ramsey.fit_ramsey_gaussian_decay(guess_tau, guess_a, (guess_f1, guess_A1, guess_phi1), (guess_f2,guess_A2, guess_phi2), (guess_f3,guess_A3, guess_phi3))

	# Plot initial guess
	# fit_xvals_0=np.linspace(0,a.sweep_pts[-1],1000)
	# ax.plot(fit_xvals_0,fitfunc_0(fit_xvals_0), 'r--', lw=1)
	#fit_xvals=np.linspace(res['x'][0],res['x'][-1],fit_num_points)

	fit_result = fit.fit1d(a.sweep_pts, a.p0.reshape(-1), ramsey.fit_ramsey_gaussian_decay,
	        guess_tau, guess_a, (guess_f1, guess_A1, guess_phi1), (guess_f2,guess_A2, guess_phi2), (guess_f3,guess_A3, guess_phi3), fixed=fixed, #,4,7,10],
	        do_print=True, ret=True)
	if fit_result != False :
		plot.plot_fit1d(fit_result, np.linspace(0,a.sweep_pts[-1],201), ax=ax,
	        plot_data=False)

	plt.savefig(os.path.join(folder, 'electronramsey_analysis.pdf'),
	        format='pdf')


	### FFT
	# p0_fft = np.fft.fft(a.p0.reshape(-1), n=32)
	# frq = np.fft.fftfreq(32, d=(a.sweep_pts[1]-a.sweep_pts[0])/1e3)
	#
	# fig = a.default_fig()
	# ax = a.default_ax(fig)
	# ax.plot(frq, p0_fft, 'o-')

def fit_Ramsey_gausscos_withoffset(timestamp = None,
	ssro_calib_folder = None,
	guess_avg = 0.5, 
	guess_A = 1./3.,
	guess_t = 10000,
	guess_a = 2,
	guess_f = 1./35,
	guess_phi = 0,
	guess_b = 1,
	fixed = [],
	fit_result = True):
	"""
	Fits cosine with offset modulated by Gaussian decay to electron Ramsey signal.
	fit func = 'avg + A *exp(-(x/t)**2) * (a * cos(2pi * (f*x + phi/360) ) + b)'
	"""

	### script
	if timestamp != None:
	    folder = toolbox.data_from_time(timestamp)
	else:
	    folder = toolbox.latest_data('ElectronRamsey')

	a = sequence.SequenceAnalysis(folder)
	a.get_sweep_pts()
	a.get_readout_results(name='ssro')
	if ssro_calib_folder != None:
		a.get_electron_ROC(ssro_calib_folder = ssro_calib_folder)
	else: 
		a.get_electron_ROC()

	# Plot data
	ax = a.plot_result_vs_sweepparam(ret='ax', name='ssro')
	# ax.set_xlim(0,1000)

	p0, fitfunc_0, fitfunc_str_0 = ramsey.fit_gaussian_decaying_cos_withoffset(guess_avg, guess_A, guess_t, guess_a, guess_f, guess_phi, guess_b)
	# Plot initial guess
	# fit_xvals_0=np.linspace(0,a.sweep_pts[-1],1000)
	# ax.plot(fit_xvals_0,fitfunc_0(fit_xvals_0), 'r--', lw=1)
	#fit_xvals=np.linspace(res['x'][0],res['x'][-1],fit_num_points)

	fit_result = fit.fit1d(a.sweep_pts, a.p0.reshape(-1), ramsey.fit_gaussian_decaying_cos_withoffset,
		guess_avg, guess_A, guess_t, guess_a, guess_f, guess_phi, guess_b,
        fixed=fixed, do_print=True, ret=True)
	
	if fit_result != False :
		plot.plot_fit1d(fit_result, np.linspace(0,a.sweep_pts[-1],2001), ax=ax,
	        plot_data=False)

	plt.savefig(os.path.join(folder, 'electronramsey_analysis.pdf'),
	        format='pdf')