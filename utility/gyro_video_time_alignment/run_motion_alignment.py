import cv2
import os
import sys
import param
import numpy as np
import matplotlib.pyplot as plt
import motion_calculation as mv_c
import ipdb
import glob

if len(sys.argv)!=2:
    print("Please enter: run_motion_alignment.py log_dir")
    exit()
else:
    log_dir = sys.argv[1]



motion_vector_path = log_dir + '/motion_vector/motion_vector.log'
gyro_log_path = log_dir + '/imu.log'
vid_meta_log_path = log_dir  + '/cs.log'

#result log path
result_dir = log_dir + '/trajectory_alignment'

if not os.path.exists(result_dir):
    os.makedirs(result_dir)


#load motion vector from image
mv_from_image = np.loadtxt(motion_vector_path)
# load raw gyro data
gyro = np.loadtxt(gyro_log_path)
# load video meta data
vid_meta = np.loadtxt(vid_meta_log_path)

# time in sec
gyro[:,0] = gyro[:,0]/param.time_scale

vid_ts_diff = np.diff(vid_meta[:,0])/param.time_scale 


mv_from_gyro = []
for i in range(min(len(mv_from_image),len(vid_meta))-1):
    # this_frame_ts = (vid_meta[i,0] - 0.5*vid_meta[i,1])/param.time_scale
    # next_frame_ts = (vid_meta[i+1,0] - 0.5*vid_meta[i+1,1])/param.time_scale
    this_frame_ts = (vid_meta[i,0])/param.time_scale
    next_frame_ts = (vid_meta[i+1,0])/param.time_scale
    
    gyro_samples = mv_c.extract_gyro_samples_from_buffer(gyro, this_frame_ts, next_frame_ts)

    angle_x, angle_y, angle_z = mv_c.cal_angular_from_angular_velocity(gyro_samples)

    mv_from_gyro.append([angle_x,angle_y,angle_z])



traj_from_gyro = np.cumsum(np.array(mv_from_gyro),axis=0)
traj_from_image = np.cumsum(mv_from_image,axis=0)

num_of_frame = min(len(traj_from_gyro),len(traj_from_image))
traj_from_image = traj_from_image[0:num_of_frame]
traj_from_gyro = traj_from_gyro[0:num_of_frame]


run_num_of_frame = 16

idx_in_xyz = np.zeros(3,dtype=int)
# calculate the closet trajectory with N frames

# trajectory between image x and gyro yaw 
min_traj_std = 9999999
for i in range(run_num_of_frame):
    if i > 0:
        traj_diff_gx = traj_from_image[:-i,1] - traj_from_gyro[i:,0]*param.focal_length
        traj_diff_gy = traj_from_image[:-i,0] + traj_from_gyro[i:,1]*param.focal_length
        traj_diff_gz = (traj_from_image[:-i,2] + traj_from_gyro[i:,2])*param.focal_length
        
    else:
        traj_diff_gx = traj_from_image[:,1] - traj_from_gyro[:,0]*param.focal_length
        traj_diff_gy = traj_from_image[:,0] + traj_from_gyro[:,1]*param.focal_length
        traj_diff_gz = (traj_from_image[:,2] + traj_from_gyro[:,2])*param.focal_length

    # traj_std_gx = np.mean(np.abs(np.diff(traj_diff_gx)))
    # traj_std_gy = np.mean(np.abs(np.diff(traj_diff_gy)))
    # traj_std_gz = np.mean(np.abs(np.diff(traj_diff_gz)))

    traj_std_gx = np.std(traj_diff_gx)
    traj_std_gy = np.std(traj_diff_gy)
    traj_std_gz = np.std(traj_diff_gz)

    traj_std = np.mean([traj_std_gx,traj_std_gy,traj_std_gz])
    
    if traj_std < min_traj_std:
        min_traj_idx = i
        min_traj_std = traj_std



plt.figure(figsize=(20, 10))
if min_traj_idx ==0:
    plt.plot(traj_from_image[:,0],label='image_x_mv')
    plt.plot(-traj_from_gyro[:,1]*param.focal_length,label='gyro_y_mv')
else:    
    plt.plot(traj_from_image[:-min_traj_idx,0],label='image_x_mv')
    plt.plot(-traj_from_gyro[min_traj_idx:,1]*param.focal_length,label='gyro_y_mv')
plt.title('alignment %d frame, trjactory between image_x and gyro yaw'%(min_traj_idx))
plt.legend()
plt.savefig("%s/traject_gy_image_x.png"%result_dir)
plt.show(block=False)
plt.pause(1)
plt.close()

plt.figure(figsize=(20, 10))
if min_traj_idx ==0:
    plt.plot(traj_from_image[:,1],label='image_y_mv')
    plt.plot(traj_from_gyro[:,0]*param.focal_length,label='gyro_x_mv')
else:
    plt.plot(traj_from_image[:-min_traj_idx,1],label='image_y_mv')
    plt.plot(traj_from_gyro[min_traj_idx:,0]*param.focal_length,label='gyro_x_mv')
plt.title('alignment %d frame, trjactory between image_y and gyro pitch'%(min_traj_idx))
plt.legend()
plt.savefig("%s/traject_gx_image_y.png"%result_dir)
plt.show(block=False)
plt.pause(1)
plt.close()

plt.figure(figsize=(20, 10))
if min_traj_idx ==0:
    plt.plot(traj_from_image[:,2],label='image_z_mv')
    plt.plot(-traj_from_gyro[:,2],label='gyro_z_mv')
else:
    plt.plot(traj_from_image[:-min_traj_idx,2],label='image_z_mv')
    plt.plot(-traj_from_gyro[min_traj_idx:,2],label='gyro_z_mv')
plt.title('alignment %d frame, trjactory between image_z and gyro roll'%(min_traj_idx))
plt.legend()
plt.savefig("%s/traject_gz_image_z.png"%result_dir)
plt.show(block=False)
plt.pause(1)
plt.close()



plt.figure(figsize=(20,10))
plt.plot(vid_ts_diff)
plt.title('video ts difference')
plt.savefig("%s/vid_ts_diff.png"%result_dir)
plt.show(block=False)
plt.pause(1)
plt.close()

alignment_idx_path = result_dir + '/align_idx.txt'

f_idx = open(alignment_idx_path,'w')
f_idx.write('%d\n'%(min_traj_idx))
f_idx.close()

print('the sample of video meta data start from  %d frame'%(min_traj_idx))

