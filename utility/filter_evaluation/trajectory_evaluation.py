import numpy as np
from scipy import signal

def trans_to_spectrum(cam_orien,fps):
    cam_orien_fft = np.fft.fft(cam_orien)
    T = 1/fps  # sampling interval 
    N = cam_orien.size

    # 1/T = frequency
    f = np.linspace(0, 1 / T, N)[:N // 2]
    amplitude = np.abs(cam_orien_fft)[:N//2]*2/N
    
    return f, amplitude

def butter_lowpass(cutoff, fs, order=6):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=6):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y


def butter_highpass(cutoff, fs, order=6):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=6):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def cal_psd(data, fs):
    
    nperseg = 64
    
    f, S = signal.welch(data, fs, nperseg=nperseg, noverlap=(nperseg // 2),detrend=None, scaling='density', window='hanning')

    return f,S/sum(S)


def cal_trajectory_sad(traj_a, traj_b):

    return np.sum(np.abs(traj_a - traj_b))


def cal_trajectory_std(traj_a, traj_b):

    return np.std(np.abs(traj_a - traj_b))


