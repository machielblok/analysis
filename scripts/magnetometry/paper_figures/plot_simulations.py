#######################################
###   PLOT Fig 4                    ###
#######################################

import matplotlib
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
execfile('D:/measuring/analysis/scripts/setup_analysis.py')
from matplotlib import rc, cm
from analysis.lib.magnetometry import adaptive_magnetometry as magnetometry
reload(magnetometry)
load_data=False

def analyze_saved_simulations (timestamp,error_bars=False):
    mgnt_exp = magnetometry.AdaptiveMagnetometry(N=14, tau0=20e-9)
    mgnt_exp.error_bars=error_bars
    mgnt_exp.load_analysis (timestamp=timestamp)
    mgnt_exp.calculate_scaling()
    return mgnt_exp


def add_scaling_plot(timestamp, ax, exp_data, label, marker_settings, color):
    #adds a scaling plot to axis 'ax', loading from analyzed data with a given 'timestamp'
    #exp_data=boolena, if 'True' then data is plotted with markers and errorbars are calculated, 
    #otherwise it is considered a simulation, and plotted like a line
    #label, string for legend
    data_file = analyze_saved_simulations (timestamp=timestamp, error_bars=exp_data)

    ax.plot (data_file.total_time, data_file.sensitivity, marker_settings,color=color, label=label)
    if exp_data: 
        ax.fill_between (data_file.total_time, data_file.sensitivity-data_file.err_sensitivity, data_file.sensitivity+data_file.err_sensitivity, color=color, alpha=0.1)
    #plt.xscale('log')
    #plt.yscale('log')
    #plt.ylabel ('$V_{H}$ T ')
    #plt.show()
    return ax

def compare_2plots(timestamp1, timestamp2, title):
    f = plt.figure(figsize=(8,6))
    ax = f.add_subplot(1,1,1)
    ax = add_scaling_plot (timestamp = timestamp1, exp_data=True, ax=ax, label = 'adapt', marker_settings='o', color='b')
    ax = add_scaling_plot (timestamp = timestamp2, exp_data=True, ax=ax, label = 'non adapt', marker_settings='^', color='r')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel ('total ramsey time [$\mu$s]', fontsize=15)
    ax.set_ylabel ('$V_{H}T$', fontsize=15)
    plt.title (title, fontsize=20)
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(15)
    plt.legend()
    plt.show()

def compare_multiple_plots(timestamps, labels, title, colours = None):
    #MAX 10 plots!!!! Then no more markers!
    f = plt.figure(figsize=(8,6))
    ax = f.add_subplot(1,1,1)
    markers = ['o', '+', '^', 'v', '>', '<', 's', '*', 'D', '|']
    ccc = np.linspace(0,1,len(timestamps))
    for i,k in enumerate(timestamps):
        if colours==None:
            c = cm.Set1(ccc[i])
        else:
            c = colours[i]
        ax = add_scaling_plot (timestamp = k, exp_data=True, ax=ax, label = labels[i], marker_settings=markers[i], color=c)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel ('total ramsey time [$\mu$s]', fontsize=15)
    ax.set_ylabel ('$V_{H}T$', fontsize=15)
    plt.title (title, fontsize=20)
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(15)
    plt.legend()
    plt.show()


def compare_G3_variableF_imperfRO():
    compare_2plots (timestamp1= '20141215_152517', timestamp2='20141215_152604', title = 'G=3, F=0, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_152820', timestamp2='20141215_152939', title = 'G=3, F=1, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_153251', timestamp2='20141215_134529', title = 'G=3, F=2, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_134649', timestamp2='20141215_134741', title = 'G=3, F=3, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_134924', timestamp2='20141215_135030', title = 'G=3, F=4, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_135229', timestamp2='20141215_135352', title = 'G=3, F=5, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_135556', timestamp2='20141215_135723', title = 'G=3, F=6, RO_fid = 0.87')


def compare_G5_variableF_imperfRO():
    compare_2plots (timestamp1= '20141215_134142', timestamp2='20141215_134205', title = 'G=5, F=0, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_134300', timestamp2='20141215_134334', title = 'G=5, F=1, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_134443', timestamp2='20141215_134529', title = 'G=5, F=2, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_134649', timestamp2='20141215_134741', title = 'G=5, F=3, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_134924', timestamp2='20141215_135030', title = 'G=5, F=4, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_135229', timestamp2='20141215_135352', title = 'G=5, F=5, RO_fid = 0.87')
    compare_2plots (timestamp1= '20141215_135556', timestamp2='20141215_135723', title = 'G=5, F=6, RO_fid = 0.87')

def compare_G5_variableF_perfRO():
    compare_2plots (timestamp1= '20141215_140947', timestamp2='20141215_141011', title = 'G=5, F=0, RO_fid = 1.00')
    compare_2plots (timestamp1= '20141215_141102', timestamp2='20141215_141139', title = 'G=5, F=1, RO_fid = 1.00')
    compare_2plots (timestamp1= '20141215_141245', timestamp2='20141215_141333', title = 'G=5, F=2, RO_fid = 1.00')
    compare_2plots (timestamp1= '20141215_141503', timestamp2='20141215_141601', title = 'G=5, F=3, RO_fid = 1.00')
    compare_2plots (timestamp1= '20141215_141745', timestamp2='20141215_141851', title = 'G=5, F=4, RO_fid = 1.00')
    compare_2plots (timestamp1= '20141215_142057', timestamp2='20141215_142214', title = 'G=5, F=5, RO_fid = 1.00')

def compare_cappellaro_varG ():
    t_stamps = ['20141215_143011','20141215_143043','20141215_143125','20141215_143221','20141215_143328','20141215_143447']
    labels = ['G=0', 'G=1', 'G=2', 'G=3', 'G=4', 'G=5']
    compare_multiple_plots (timestamps=t_stamps, labels=labels, title = 'Cappellaro protocol (F=0, RO_fid=1)')

def compare_swarm_opt ():
    t_stamps = ['20141215_161225','20141218_155251','20141216_035209']
    labels = ['G=5, F=2 capp', 'G=5, F=2 swarm', 'G=5, F=7 non_adptv']
    colours = ['b', 'r', 'k']
    compare_multiple_plots (timestamps=t_stamps, labels=labels, title = 'compare protocols', colours=colours)



#compare_G5_variableF_imperfRO()
#compare_G5_variableF_perfRO()
#compare_cappellaro_varG()
compare_swarm_opt()
