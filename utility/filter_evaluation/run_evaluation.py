import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import trajectory_evaluation as traj_eval
import matplotlib.ticker as ticker
from scipy import signal

os.system('cp -rf ../../code/python/eis_core ./')
os.system('cp ../../code/python/config_path.py ./')

from eis_core import eis_core_config_loader
import config_path

if len(sys.argv) !=2:
    print("Please enter: python run_evaluation.py log_dir")
else:

    log_dir = sys.argv[1]

dir_name = log_dir.split('/')[-1]


fps = 30
cutoff = 0.5

# load debug/eis param
debug_param = eis_core_config_loader.load_debug_config(config_path.debug_config_path)
eis_param = eis_core_config_loader.load_eis_config(config_path.eis_config_path)

#result log path
if eis_param.use_nonlinear_filter:
    result_dir = log_dir + '/result' + '_nonlinear_alpha_min_%.2f_max_%.2f_beta_%.2f_gamma_%.2f_inner_ratio_%.1f_lookahead_%d_crop_ratio_%.1f'\
    %(eis_param.alpha_min,eis_param.alpha_max,eis_param.beta,eis_param.gamma,eis_param.inner_padding_ratio,eis_param.lookahead_no,eis_param.crop_ratio) 
else:
    result_dir = log_dir + '/result' + '_const_lpf_alpha_%.2f_inner_ratio_%.1f_lookahead_%d_crop_ratio_%.1f'%(eis_param.alpha,eis_param.inner_padding_ratio,eis_param.lookahead_no,eis_param.crop_ratio) 

if not os.path.exists(result_dir):
    os.makedirs(result_dir)
    
v_cam_path = result_dir + '/v_cam_orien.log'
p_cam_path = result_dir + '/p_cam_orien.log'
report_path = result_dir + '/filter_evaluation.csv'
final_score_path = log_dir + '/tmp_final_score.log'

final_score_log = open(final_score_path,mode='w+')
eval_report = open(report_path,mode='w+')
eval_report.write(',score1,score2,score\n')


v_cam_orien = np.loadtxt(v_cam_path)
p_cam_orien = np.loadtxt(p_cam_path)


plot_on = True
avg_score = 0
avg_score_1 = 0 
avg_score_2 = 0 
for i in range(3):

    p_cam_orien_in_axis = p_cam_orien[:,i]
    v_cam_orien_in_axis = v_cam_orien[:,i]

    # make a golden camera oreintation
    golden_cam_orien = traj_eval.butter_lowpass_filter(p_cam_orien_in_axis, cutoff, fps)
    
    # analyze PSD of camera orienation
    f,golden_cam_orien_psd = traj_eval.cal_psd(np.diff(golden_cam_orien), fps)
    f,p_cam_orien_psd = traj_eval.cal_psd(np.diff(p_cam_orien_in_axis), fps)
    f,v_cam_orien_psd = traj_eval.cal_psd(np.diff(v_cam_orien_in_axis), fps)

    #score 1
    golden_cam_freq_mag = np.sum(f*golden_cam_orien_psd)
    p_cam_freq_mag = np.sum(f*p_cam_orien_psd)
    v_cam_freq_mag = np.sum(f*v_cam_orien_psd)
    score1 = (p_cam_freq_mag-v_cam_freq_mag)/(p_cam_freq_mag-golden_cam_freq_mag)
    
    # calcuate the jitter between golden and physical camera trajectory, which means the total jitter 
    total_jitter = np.abs(golden_cam_orien-p_cam_orien_in_axis)
    # calcuate the jitter between physical and virtual camera trajectory, which means the removed jitter 
    comp_jitter = np.abs(v_cam_orien_in_axis- p_cam_orien_in_axis)
    
    # score 1 is for measurement the distance of camera trajectory
    jitter_ratio = total_jitter/(comp_jitter+0.0001)
    idx = np.where(jitter_ratio >1)
    jitter_ratio[idx] = 1
    score2 = np.mean(jitter_ratio)
    
    score = 0.6*score1 + 0.4*score2 
    
    print('score1 = %.2f, score2 = %.2f, score = %.2f'%(score1,score2,score))
    avg_score += score
    avg_score_1 += score1
    avg_score_2 += score2
    
    eval_report.write('cam_axis_%d,%.2f,%.2f,%.2f\n'%(i,score1,score2,score))

   
    if plot_on:
    
        fig = plt.figure(figsize=(30,15))
        plt.subplot(3,1,1)
        plt.bar(f,p_cam_orien_psd,label='p_cam_psd',width=0.4,color='orange')
        plt.xlabel('frequency')
        plt.ylabel('psd')
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.5))
        plt.title('psd*freq mag = %.2f'%p_cam_freq_mag,loc='right')
        plt.legend()

        plt.subplot(3,1,2)
        plt.bar(f,golden_cam_orien_psd,label='golden_cam_psd',width=0.4,color='b')
        plt.xlabel('frequency')
        plt.ylabel('psd')
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.5))
        plt.title('psd*freq mag = %.2f'%golden_cam_freq_mag,loc='right')
        plt.legend()
        
        plt.subplot(3,1,3)
        plt.bar(f,v_cam_orien_psd,label='v_cam_psd',width=0.4,color='g')
        plt.xlabel('frequency')
        plt.ylabel('psd')
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.5))
        plt.title('psd*freq mag = %.2f'%v_cam_freq_mag,loc='right')
        plt.legend()
        plt.suptitle('score1=%.2f'%score1)
        plt.savefig("%s/psd_analysis_axis_%d.png"%(result_dir,i))
        if debug_param.show_plot:
            plt.show(block=False)
            plt.pause(1)
        plt.close(fig)

        fig = plt.figure(figsize=(30, 15))
        plt.subplot(3,1,1)
        plt.plot(golden_cam_orien,label='golden_cam_orien[%d]'%i,linewidth=3)
        plt.plot(p_cam_orien_in_axis,label='p_cam_orien[%d]'%i)
        plt.plot(v_cam_orien_in_axis,label='v_cam_orien[%d]'%i)
        plt.xlabel('sample')
        plt.ylabel('rad')
        plt.legend()
        
        plt.subplot(3,1,2)
        plt.plot(total_jitter,label='total_jitter')
        plt.plot(comp_jitter,label='compensate_jitter',color='g')
        plt.xlabel('sample')
        plt.ylabel('rad')
        plt.legend()
        
        plt.subplot(3,1,3)
        plt.plot(jitter_ratio, label='total_jitter/over_comp_jitter',color='black')
        plt.hlines(1,0,len(jitter_ratio),linestyles='-.',color='r')
        plt.ylim([-0.5,1.5])
        plt.xlabel('sample')
        plt.ylabel('rad')
        plt.legend()
        plt.suptitle('score2 = %.2f'%score2)
        
        plt.savefig("%s/jitter_analysis_axis_%d.png"%(result_dir,i))
        if debug_param.show_plot:
            plt.show(block=False)
            plt.pause(1)
        plt.close(fig)

  
avg_score = avg_score/3
avg_score_1 = avg_score_1/3
avg_score_2 = avg_score_2/3

print('average: score1 = %.3f, score2 = %.3f, score = %.3f'%(avg_score_1,avg_score_2,avg_score))
eval_report.write('average,%.3f, %.3f, %.3f'%(avg_score_1,avg_score_2,avg_score))
eval_report.close()

final_score_log.write('%.3f'%avg_score)
final_score_log.close()

os.system('rm -rf eis_core')
os.system('rm config_path.py')