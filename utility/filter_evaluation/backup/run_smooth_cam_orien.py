import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
import trajectory_evaluation as traj_eval
import ipdb

if len(sys.argv) !=2:
    print("Please enter: python run_evaluation.py log_dir")
else:

    log_dir = sys.argv[1]

fps = 30
nperseg = 64    # even
v_cam_path = log_dir + '/v_cam_orien.log'
p_cam_path = log_dir + '/p_cam_orien.log'


v_cam_orien = np.loadtxt(v_cam_path)
p_cam_orien = np.loadtxt(p_cam_path)

cutoff = 0.85

p_cam_orien_axis = p_cam_orien[:,2]
v_cam_orien_axis = v_cam_orien[:,2]
smooth_p_cam_orien = traj_eval.butter_lowpass_filter(p_cam_orien_axis,cutoff,fps)
hp_p_cam_orien = traj_eval.butter_highpass_filter(p_cam_orien_axis, cutoff, fps)
hp_v_cam_orien = traj_eval.butter_highpass_filter(v_cam_orien_axis, cutoff, fps)


# Compute PSD with `scipy.signal.welch`
f_p_cam, S_p_cam = welch(hp_p_cam_orien, fs=fps, nperseg=nperseg, noverlap=(nperseg // 2),detrend=None, scaling='density', window='hanning')
f_v_cam, S_v_cam = welch(hp_v_cam_orien, fs=fps, nperseg=nperseg, noverlap=(nperseg // 2),detrend=None, scaling='density', window='hanning')
f_sp_cam, S_sp_cam = welch(smooth_p_cam_orien, fs=fps, nperseg=nperseg, noverlap=(nperseg // 2),detrend=None, scaling='density', window='hanning')


# plt.loglog(f_p_cam,S_p_cam,label='p_cam')
# plt.loglog(f_sp_cam,S_sp_cam,label='sp_cam')
# plt.loglog(f_v_cam,S_v_cam,label='v_cam')
# plt.plot(f_p_cam[nperseg//4:],S_p_cam[nperseg//4:],label='p_cam')
# plt.plot(f_sp_cam[nperseg//4:],S_sp_cam[nperseg//4:],label='sp_cam')
# plt.plot(f_v_cam[nperseg//4:],S_v_cam[nperseg//4:],label='v_cam')

plt.plot(f_p_cam[nperseg//4:],S_p_cam[nperseg//4:],label='p_cam')
plt.plot(f_v_cam[nperseg//4:],S_v_cam[nperseg//4:],label='v_cam')

plt.legend()
plt.show()

ipdb.set_trace()
# label_txt = 'p_cam_orien_in_cutoff+%.2f'%cutoff
# plt.plot(p_cam_orien_asix,label='p_cam_orien')
# plt.plot(v_cam_orien_asix,label='v_cam_orien')
# plt.plot(smooth_p_cam_orien,label=label_txt)

# plt.legend()
# plt.show()