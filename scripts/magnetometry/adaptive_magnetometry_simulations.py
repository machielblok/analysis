
import numpy as np
from analysis.lib.fitting import fit, ramsey, common
from analysis.lib.tools import plot
import random
from matplotlib import rc, cm
import os, sys
import h5py
import logging, time

from matplotlib import pyplot as plt
from analysis.lib import fitting
#from analysis.lib.m2.ssro import sequence
#from analysis.lib.tools import toolbox
##from analysis.lib.fitting import fit,esr
from analysis.lib.tools import plot
from matplotlib import rc, cm
from analysis.lib.magnetometry import adaptive_magnetometry as magnetometry

reload(magnetometry)

def simulate_cappellaro ():
	maj_reps = 5
	M = 5

	set_magnetic_field =-22.1875e6
	s = magnetometry.RamseySequence_Simulation (N_msmnts = 7, reps=200, tau0=20e-9)

	s.setup_simulation (magnetic_field_hz = set_magnetic_field, M=M)
	s.T2 = 96e-6
	s.fid0 = 0.868
	s.fid1 = 1-0.978
	s.renorm_ssro = True
	s.maj_reps = maj_reps
	s.maj_thr = 1

	s.table_based_simulation()
	#s.sim_cappellaro_majority()
	s.convert_to_dict()
	s.print_table_positions()
		
	beta, p, err,a, b = s.mean_square_error(set_value=set_magnetic_field, do_plot=True)

	s.sim_cappellaro_majority()
	s.convert_to_dict()
	s.print_results()
	beta, p, err,a,b = s.mean_square_error(set_value=set_magnetic_field, do_plot=True)



def simulate_nonadaptive ():
	set_magnetic_field = 4e6 
	s = magnetometry.RamseySequence_Simulation (N_msmnts = 7, reps=100, tau0=20e-9)

	s.setup_simulation (magnetic_field_hz = set_magnetic_field, M=M)
	s.T2 = 96e-6
	s.fid0 = 0.9
	s.fid1 = 0.02
	s.renorm_ssro = False
	s.maj_reps = maj_reps
	s.maj_thr = 1
	#s.table_based_simulation()
	s.sim_cappellaro_majority()
	s.convert_to_dict()
	s.print_results()
		
	beta, p, err,a,b = s.mean_square_error(set_value=set_magnetic_field, do_plot=True)


def simulate_sweep_field(N,M, maj_reps, maj_thr, fid0):

	#try:
	print '############### Simulate #####################'
	mgnt_exp = magnetometry.AdaptiveMagnetometry(N=N, tau0=20e-9)
	mgnt_exp.set_protocol (M=M, maj_reps = maj_reps, maj_thr = maj_thr)
	mgnt_exp.set_sweep_params (reps =20, nr_periods = 5, nr_points_per_period=25)
	mgnt_exp.set_exp_params( T2 = 96e-6, fid0 = fid0, fid1 = 0.02)
	#for n in np.arange(N-1)+2:
	mgnt_exp.sweep_field_simulation (N=1)
	plt.figure()
	mgnt_exp.plot_msqe_dictionary(y_log=True)
	mgnt_exp.plot_sensitivity_scaling()
	mgnt_exp.save()
	#except:
	#	print 'Simulation failed!!'


def analyze_saved_simulations (timestamp):
	mgnt_exp = magnetometry.AdaptiveMagnetometry(N=6, tau0=20e-9)
	mgnt_exp.load_analysis (timestamp=timestamp)
	mgnt_exp.plot_msqe_dictionary(y_log=True, save_plot=True)
	mgnt_exp.plot_sensitivity_scaling(save_plot=True)

#analyze_saved_simulations (timestamp='20141017_003446')

def simulate_adwin ():
	N = 7
	pp = int(np.random.randint(1, 2**(N-1)))
	set_magnetic_field = pp*(1/20e-9)/(2**N) 
	print 'B-field:', set_magnetic_field/1e6
	s = magnetometry.RamseySequence_Adwin (N_msmnts = N, reps=20, tau0=20e-9)

	s.setup_simulation (magnetic_field_hz = set_magnetic_field, M=5)
	s.T2 = 96e-6
	s.fid0 = 1.00
	s.fid1 = 0.0
	s.renorm_ssro = False
	s.maj_reps = 1
	s.maj_thr = 0
	
	s.adwin_ultrafast()
	s.convert_to_dict()
	s.print_results()
	beta, p, err,a, b = s.mean_square_error(set_value=set_magnetic_field, do_plot=False)

	plt.figure()
	#plt.plot (beta_adwin, p_adwin, 'b')
	plt.plot (beta*1e-6, p, 'r')
	plt.show()


def check_adwin_code (N,M, msmnt_results):
	s = magnetometry.RamseySequence_Adwin (N_msmnts = N, reps=1, tau0=20e-9)
	s.setup_simulation (magnetic_field_hz = 0, M=M)
	s.T2 = 96e-6
	s.fid0 = 1.00
	s.fid1 = 0.0
	s.renorm_ssro = False
	s.maj_reps = 1
	s.maj_thr = 0	
	s.adwin_ultrafast_print_steps (msmnt_results = msmnt_results)


def benchmark_exec_speed ():

	nr_N=10
	tempo_brute = np.zeros(nr_N)
	tempo_positive  = np.zeros(nr_N)
	tempo_nonzero = np.zeros(nr_N)
	tempo_ultrafast = np.zeros(nr_N)

	ind = 0
	for n in np.arange (nr_N)+2:
		print '##### ',n
		set_magnetic_field = 2*(1/20e-9)/(2**n) 
		s = magnetometry.RamseySequence_Adwin (N_msmnts = n, reps=10, tau0=20e-9)

		s.setup_simulation (magnetic_field_hz = set_magnetic_field, M=1)
		s.T2 = 96e-6
		s.fid0 = 1.00
		s.fid1 = 0.00
		s.renorm_ssro = False
		s.maj_reps = 1
		s.maj_thr = 0
		ex1 = s.basic_adwin_algorithm(exec_speed = True)
		tempo_brute[ind] = ex1
		ex2 = s.adwin_only_positive(exec_speed = True)
		tempo_positive[ind] = ex2
		ex3 = s.adwin_positive_nonzero(exec_speed = True)
		tempo_nonzero[ind] = ex3
		ex4 = s.adwin_ultrafast(exec_speed = True)
		tempo_ultrafast[ind] = ex4
		ind +=1

	plt.semilogy (np.arange (nr_N)+2, tempo_brute, linewidth=2, label = 'brute force')
	plt.semilogy (np.arange (nr_N)+2, tempo_positive, linewidth=2, label = 'only k>0')
	plt.semilogy (np.arange (nr_N)+2, tempo_nonzero, linewidth=2, label = 'k>0, p[k] not 0')
	plt.semilogy (np.arange (nr_N)+2, tempo_ultrafast, linewidth=2, label = 'ultrafast')
	plt.xlabel ('N')
	plt.ylabel ('execution time [s]')
	plt.legend()
	plt.show()

def adwin_phase_angle (real_part, imag_part):

		c_nr = real_part+1j*imag_part

		if (real_part>0):
			if (imag_part>0):
				th = (180/np.pi)*np.arctan (imag_part/real_part)
			else:
				th = (180/np.pi)*np.arctan (imag_part/real_part)+360
		else:
			if (imag_part>0):
				th = 180-(180/np.pi)*np.arctan (-imag_part/real_part)
			else:
				th = 180+(180/np.pi)*np.arctan (imag_part/real_part)

		print 'Number :', c_nr
		print 'Using python angle: ', np.mod((180/np.pi)*np.angle(c_nr), 360)
		print 'Using arctan: ', th


#simulate_sweep_field (N=1, M=3, maj_reps=5, maj_thr=1, fid0=0.95)
'''
simulate_sweep_field (N=9, M=4, maj_reps=7, maj_thr=2, fid0=0.87)
simulate_sweep_field (N=10, M=3, maj_reps=6, maj_thr=2, fid0=0.87)
simulate_sweep_field (N=9, M=4, maj_reps=6, maj_thr=2, fid0=0.87)
simulate_sweep_field (N=10, M=3, maj_reps=5, maj_thr=1, fid0=0.87)
simulate_sweep_field (N=9, M=4, maj_reps=5, maj_thr=1, fid0=0.87)
'''
check_adwin_code(N=4, M=1, msmnt_results = [1,1,1,1])
#benchmark_exec_speed()

#adwin_phase_angle (real_part=-0.5, imag_part=-1)