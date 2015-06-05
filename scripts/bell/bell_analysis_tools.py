import numpy as np
import os
import datetime
import analysis.lib.tools.toolbox as tb
from analysis.lib.lde import ro_c_err
from analysis.lib.bell import bell_events as be

   #corr defs
rnd_corr=[[0,0],[0,1],[1,0],[1,1]] #'RND [LT3,LT4] rnd 00,01,10,11'
ro_corr =[[1,1],[1,0],[0,1],[0,0]] #'RO [LT3,LT4] ms  00, 01, 10, 11'

def correlator_error(N00,N01,N10,N11):
    return 2*np.sqrt((N00**3*(N01+N10)+N00**2*(2*N01*N10+3*(N01+N10)*N11)+N11*((N01+N10)**3+2*N01*N10*N11+(N01+N10)*N11**2)+N00*((N01+N10)**3+2*(N01**2+4*N01*N10+N10**2)*N11+3*(N01+N10)*N11**2))/(N00+N01+N10+N11)**5)

def RO_correct(RO_norm, F0A, F1A, F0B, F1B):
    RO_norm =np.asmatrix(RO_norm)
    U = np.matrix([[F0A*F0B,         F0A*(1-F1B),     F0B*(1-F1A),     (1-F1A)*(1-F1B)],
                   [F0A*(1-F0B),     F0A*F1B,         (1-F1A)*(1-F0B), F1B*(1-F1A)],
                   [F0B*(1-F0A),     (1-F0A)*(1-F1B), F1A*F0B,         F1A*(1-F1B)],
                   [(1-F0A)*(1-F0B), F1B*(1-F0A),     F1A*(1-F0B),     F1A*F1B]])
    Uinv=U.I
    return np.matrix.dot(Uinv,RO_norm.T)

def RO_correct_err(RO_norm, F0A, F1A, F0B, F1B):
    (N00, N01, N10, N11) = RO_norm
    return np.array(ro_c_err.get_readout_correction_errors(F0a=F0A,F1a=F1A, F0b=F0B, F1b=F1B, dF0a = 0.005,dF1a = 0.005,dF0b = 0.005,dF1b = 0.005,N00=N00, N01=N01,N10=N10, N11=N11))

def RO_correct_single_qubit(p0,u_p0, F0=0.955, F1=0.98):
    roc = error.SingleQubitROC()
    roc.F0, roc.u_F0, roc.F1, roc.u_F1 = (F0,0.005,F1,0.005)
    c0, u_c0 = roc.num_eval(p0,u_p0)
    return c0,u_c0 


def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def print_correlators(corr_mats):
    # print the results:
    for psi in ['psi_min', 'psi_plus']:
        corr_mat=np.zeros((4,4))
        for k in corr_mats:
            if psi in k:
                corr_mat+=corr_mats[k]
        noof_ev_fltr = int(np.sum(corr_mat))
                
        Es=np.zeros(4)
        dEs=np.zeros(4)

        for i,rnd in enumerate(rnd_corr):
            Es[i] = (corr_mat[i,0] - corr_mat[i,1] - corr_mat[i,2] + corr_mat[i,3])/float(np.sum(corr_mat[i,:]))
            dEs[i] = correlator_error(corr_mat[i,0],corr_mat[i,1],corr_mat[i,2],corr_mat[i,3])
            
        if psi == 'psi_min':
            expected_Es= (-0.42,0.42,0.67,0.67)
            CHSH  = -Es[0] + Es[1] + Es[2] + Es[3]
        elif psi == 'psi_plus':
            expected_Es= (0.42,-0.42,0.67,0.67)
            CHSH  = Es[0] - Es[1] + Es[2] + Es[3]
        dCHSH = np.sqrt(dEs[0]**2 + dEs[1]**2 + dEs[2]**2 + dEs[3]**2)
        
        print '-'*40
        print 'FILTERED EVENTS {}: Number of events {}'.format(psi,noof_ev_fltr)
        print 'RO ms   00, 01, 10, 11'
        print 'RND00', corr_mat[0], '  +pi/2, +3pi/4'
        print 'RND01', corr_mat[1], '  +pi/2, -3pi/4'
        print 'RND10', corr_mat[2], '  0,     +3pi/4'
        print 'RND11', corr_mat[3], '  0,     -3pi/4\n'

        print ' E (RND00  RND01  RND10  RND11 )'
        print '   ({:+.2f}, {:+.2f}, {:+.2f}, {:+.2f}) expected'.format(*expected_Es)
        print '   ({:+.2f}, {:+.2f}, {:+.2f}, {:+.2f}) measured'.format(*Es)
        print '+/-( {:.2f},  {:.2f},  {:.2f},  {:.2f} )'.format(*dEs)

        print 'CHSH : {:.2f} +- {:.2f}'.format(CHSH, dCHSH)

def C_val(x,y,a,b,psi):#expects binary inputs.
    if ('psi_min' in psi) and (x==0) and (y==0):
        #print 'psi_min', x,y,a,b,(a+b)%2
        return (a+b)%2
    elif ('psi_plus' in psi) and (x==0) and (y==1):
        #print 'psi_plus', x,y,a,b,(a+b)%2
        return (a+b)%2
    else:
        #print 'else', x,y,a,b, (a+b+1)%2
        return (a+b+1)%2

def calculate_p_lhv(corr_mats):
    K = 0
    N = 0
    Kxx = 0
    Nxx = 0
    Kzz = 0
    Nzz = 0
    for i,rnd in enumerate(rnd_corr):
        for j,ro in enumerate(ro_corr):
            for psi in corr_mats:
                C=C_val(rnd[0], rnd[1], ro[0], ro[1], psi)
                k=(C==1)*corr_mats[psi][i,j]
                n=corr_mats[psi][i,j]
                K+=k
                N+=n
                if rnd[0] == 0: #LT3 did a pi/2 pulse
                    Kxx+=k
                    Nxx+=n
                elif rnd[0] == 1: #LT3 did no pi/2 pulse
                    Kzz+=k
                    Nzz+=n
                    
    print 'All: {}/{} = {:.2f}'.format(K, N, K/N)
    from scipy.stats import binom
    p_lhv = 1- binom.cdf(K, N, 3./4)
    print 'Probability of LHV model: {:.1f}%'.format(p_lhv*100)
    print 'XX: {}/{} = {:.2f}'.format(Kxx, Nxx, Kxx/Nxx)
    print 'ZZ: {}/{} = {:.2f}'.format(Kzz, Nzz, Kzz/Nzz)

def get_sp_corrs(db,dlt,db_fps, analsysis_params, lt3):
    st_start_ch0  = analsysis_params['st_start_ch0']
    st_len        = analsysis_params['st_len'] #50 ns
    st_len_w2     = st_len
    p_sep         = analsysis_params['pulse_sep'] #600 ns
    st_start_ch1  = analsysis_params['st_start_ch1']
            
    st_fltr_w1 =  (((st_start_ch0 <= db[:,be._cl_st_w1]) & (db[:,be._cl_st_w1] < (st_start_ch0 + st_len)) & (db[:,be._cl_ch_w1] == 0)) \
                 | ((st_start_ch1 <= db[:,be._cl_st_w1]) & (db[:,be._cl_st_w1] < (st_start_ch1 + st_len)) & (db[:,be._cl_ch_w1] == 1)) )  
    st_fltr_w2 =  (((st_start_ch0 + p_sep <= db[:,be._cl_st_w2]) & (db[:,be._cl_st_w2] < (st_start_ch0 + p_sep + st_len_w2)) & (db[:,be._cl_ch_w2] == 0)) \
                 | ((st_start_ch1 + p_sep <= db[:,be._cl_st_w2]) & (db[:,be._cl_st_w2] < (st_start_ch1 + p_sep + st_len_w2)) & (db[:,be._cl_ch_w2] == 1)) )   

    no_invalid_mrkr_fltr = (d3[:,be._cl_inv_mrkr]==0) & (d4[:,be._cl_inv_mrkr]==0)

    sp_names=['w1','w2']
    sp_fltrs = [st_fltr_w1,st_fltr_w2]
    valid_event_fltr_SP = (db[:,be._cl_type] == 2) | (db[:,be._cl_type] == 3)
    st_fltr = st_fltr_w1 | st_fltr_w2
    dt_fltr = True
    rnd_fltr = (dlt[:,be._cl_noof_rnd_0] + dlt[:,be._cl_noof_rnd_1] == 1 )
    corr_mats={}
    for psi_name,psi_fltr in zip(sp_names,sp_fltrs):
        fltr = valid_event_fltr_SP & rnd_fltr & psi_fltr & no_invalid_mrkr_fltr
        db_fltr = db[fltr]
        dlt_fltr = dlt[fltr]
        noof_ev_fltr = np.sum(fltr)
        p0 = np.sum(dlt_fltr[:,be._cl_noof_ph_ro]>0)
        u_p0 = np.sqrt(p0*(1-p0)/noof_ev_fltr)
        p0_corr, u_p0_corr = RO_correct_single_qubit(p0,u_p0)
        corr_mats[psi_name] = [p0,u_p0,p0_corr,u_p0_corr]
    return corr_mats



def get_corr_mats(db,d3,d4, db_fps, analsysis_params, bad_time_ranges):
    #Windows & other filtes:
    st_start_ch0  = analsysis_params['st_start_ch0']
    st_len        = analsysis_params['st_len'] #50 ns
    st_len_w2_00  = analsysis_params['st_len_w2_00']
    st_len_w2_11  = analsysis_params['st_len_w2_11']
    p_sep         = analsysis_params['pulse_sep'] #600 ns
    st_start_ch1  = analsysis_params['st_start_ch1']
        
    #bad times due to lights on at EWI
    event_times = []
    bad_time_fltr = np.ones(len(db), dtype=np.bool)

    for i in range(len(db)):
        event_time = tb.get_datetime_from_folder(os.path.split(db_fps[i])[0]) \
                    + datetime.timedelta(seconds = db[i,be._cl_tt_w1]/1e12)
        event_times.append(event_time)
        for bad_time_range in bad_time_ranges:
            bad_time_fltr[i] = (bad_time_fltr[i]) and ((event_time <=  bad_time_range[0]) or (event_time >  bad_time_range[1]))
    print 'Events in bad time ranges: {}/{}'.format(len(db)-np.sum(bad_time_fltr), len(db))

    #invalid data marker filter & BS invalid event filter
    no_invalid_mrkr_fltr = (d3[:,be._cl_inv_mrkr]==0) & (d4[:,be._cl_inv_mrkr]==0)
    valid_event_fltr = db[:,be._cl_type] == 1
    rnd_fltr = (d3[:,be._cl_noof_rnd_0] + d3[:,be._cl_noof_rnd_1] == 1 ) \
                 & (d4[:,be._cl_noof_rnd_0] + d4[:,be._cl_noof_rnd_1] == 1 ) 
    psb_tail_fltr = (d3[:,be._cl_noof_ph_tail] == 0) & (d4[:,be._cl_noof_ph_tail] == 0)

    #BS event channels
    psi_plus_00_fltr = (db[:,be._cl_ch_w1] == 0) & (db[:,be._cl_ch_w2] == 0)
    psi_min_01_fltr  = (db[:,be._cl_ch_w1] == 0) & (db[:,be._cl_ch_w2] == 1)
    psi_min_10_fltr  = (db[:,be._cl_ch_w1] == 1) & (db[:,be._cl_ch_w2] == 0)
    psi_plus_11_fltr = (db[:,be._cl_ch_w1] == 1) & (db[:,be._cl_ch_w2] == 1)
    psi_filters = [psi_plus_00_fltr,psi_min_01_fltr,psi_min_10_fltr,psi_plus_11_fltr]
    psi_names = ['psi_plus_00','psi_min_01','psi_min_10','psi_plus_11']

    corr_mats={}
    for psi_name,psi_fltr in zip(psi_names,psi_filters):
        if 'psi_min' in psi_name:
            st_len_w2 = st_len
        elif 'psi_plus_00' in psi_name:
            st_len_w2 = st_len_w2_00
        elif 'psi_plus_11' in psi_name:
             st_len_w2 = st_len_w2_11
                
        st_fltr_w1 =  (((st_start_ch0 <= db[:,be._cl_st_w1]) & (db[:,be._cl_st_w1] < (st_start_ch0 + st_len)) & (db[:,be._cl_ch_w1] == 0)) \
                     | ((st_start_ch1 <= db[:,be._cl_st_w1]) & (db[:,be._cl_st_w1] < (st_start_ch1 + st_len)) & (db[:,be._cl_ch_w1] == 1)) )  
        st_fltr_w2 =  (((st_start_ch0 + p_sep <= db[:,be._cl_st_w2]) & (db[:,be._cl_st_w2] < (st_start_ch0 + p_sep + st_len_w2)) & (db[:,be._cl_ch_w2] == 0)) \
                     | ((st_start_ch1 + p_sep <= db[:,be._cl_st_w2]) & (db[:,be._cl_st_w2] < (st_start_ch1 + p_sep + st_len_w2)) & (db[:,be._cl_ch_w2] == 1)) )   
        st_fltr = st_fltr_w1 & st_fltr_w2

        fltr = st_fltr & psi_fltr  & valid_event_fltr  & rnd_fltr & no_invalid_mrkr_fltr & psb_tail_fltr & bad_time_fltr
            
        db_fltr = db[fltr]
        d3_fltr = d3[fltr]
        d4_fltr = d4[fltr]
        noof_ev_fltr = np.sum(fltr)   
        
        corr_mat=np.zeros((4,4))

        for i,rnd in enumerate(rnd_corr):
            for j,ro in enumerate(ro_corr):
                corr_mat[i,j] =np.sum( ( d3_fltr[:,be._cl_noof_rnd_1]      == rnd[0]) \
                                     & ( d4_fltr[:,be._cl_noof_rnd_1]      == rnd[1]) \
                                     & ((d3_fltr[:,be._cl_noof_ph_ro] > 0) == ro[0] ) \
                                     & ((d4_fltr[:,be._cl_noof_ph_ro] > 0) == ro[1]))
        corr_mats[psi_name] = corr_mat
    
    return corr_mats

def print_ZZ_fidelity(corr_mats, analsysis_params):
    for psi in ['psi_min', 'psi_plus']:
        corr_mat=np.zeros((4,4))
        for k in corr_mats:
            if psi in k:
                corr_mat+=corr_mats[k]
        noof_ev_fltr = int(np.sum(corr_mat))

        Ng_ZZ = corr_mat[0,1] + corr_mat[0,2] +corr_mat[1,0] + corr_mat[1,3] + corr_mat[2,0] + corr_mat[2,3] + corr_mat[3,1] + corr_mat[3,2] #for ZZ with RND
        corr_mat_RO_corr=np.zeros((4,4))
        for i in range(4) : 
            RO_row = corr_mat[i]
            RO_row_corr= RO_correct(RO_row/float(noof_ev_fltr),
                                    F0A =analsysis_params['F0A'], F1A =analsysis_params['F1A'],
                                    F0B =analsysis_params['F0B'], F1B =analsysis_params['F1B'] )
            for j in range(4):
                corr_mat_RO_corr[i,j] = RO_row_corr[j]
        Ng_ZZ_RO_corr = corr_mat_RO_corr[0,1] + corr_mat_RO_corr[0,2] +corr_mat_RO_corr[1,0] + corr_mat_RO_corr[1,3] \
                        + corr_mat_RO_corr[2,0] + corr_mat_RO_corr[2,3] + corr_mat_RO_corr[3,1] + corr_mat_RO_corr[3,2]
        RO_corr = np.zeros(4)
        RO_corr[0] = corr_mat_RO_corr[0,0] + corr_mat_RO_corr[1,1] +corr_mat_RO_corr[2,1] + corr_mat_RO_corr[3,0]
        RO_corr[1] = corr_mat_RO_corr[0,1] + corr_mat_RO_corr[1,0] +corr_mat_RO_corr[2,0] + corr_mat_RO_corr[3,1]
        RO_corr[2] = corr_mat_RO_corr[0,2] + corr_mat_RO_corr[1,3] +corr_mat_RO_corr[2,3] + corr_mat_RO_corr[3,2]
        RO_corr[3] = corr_mat_RO_corr[0,3] + corr_mat_RO_corr[1,2] +corr_mat_RO_corr[2,1] + corr_mat_RO_corr[3,3]

        Fid = Ng_ZZ/noof_ev_fltr
        dFid = np.sqrt(Fid*(1-Fid)/noof_ev_fltr)
        Fid_corr= Ng_ZZ_RO_corr
        
        print '-'*40
        print 'FILTERED EVENTS {}: Number of events {}'.format(psi,noof_ev_fltr)
        print 'Fidelity: {:.2f}% +- {:.1f}%'.format(Fid*100,dFid*100)
        print 'Corrected fidelity: {:.2f}%'.format(Fid_corr*100)


        