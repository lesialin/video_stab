import matplotlib.pyplot as plt
import numpy as np
import sys
import glob
import os
import cv2
import ipdb
import shutil

os.system('cp -rf ../../code/python/eis_core ./')
os.system('cp ../../code/python/config_path.py ./')

from eis_core import eis_core_config_loader
import config_path

if len(sys.argv)!=2:
    print("Please enter: run_analysis.py log_dir")
    exit()
else:
    log_dir = sys.argv[1]

OOB_ON = False
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
    
vid_stab_log_path = log_dir + '/vid_stab.log'
v_cam_orien_path = log_dir + '/v_cam_orien.log'
p_cam_orien_path = log_dir + '/p_cam_orien.log'
out_of_boundary_path = log_dir + '/out_of_boundary.log'
alpha_path = log_dir + '/alpha.log'
uncompensated_dist_path = log_dir + '/uncompensated_dist.log'

v_cam_orien = np.loadtxt(v_cam_orien_path)
p_cam_orien = np.loadtxt(p_cam_orien_path)
out_of_boundary = np.loadtxt(out_of_boundary_path)
alpha = np.loadtxt(alpha_path)
uncompensated_dist = np.loadtxt(uncompensated_dist_path)


# move the analysis log to result directory
shutil.copy(vid_stab_log_path, result_dir)
shutil.copy(v_cam_orien_path, result_dir)
shutil.copy(p_cam_orien_path, result_dir)
shutil.copy(out_of_boundary_path, result_dir)
shutil.copy(uncompensated_dist_path, result_dir)
shutil.copy(alpha_path, result_dir)

os.remove(vid_stab_log_path)
os.remove(v_cam_orien_path)
os.remove(p_cam_orien_path)
os.remove(out_of_boundary_path)
os.remove(uncompensated_dist_path)
os.remove(alpha_path)

# start to plot figure!!!
fig = plt.figure(figsize=(20, 10))
plt.plot(p_cam_orien[:,0], label='p_cam_orien_x')
plt.plot(v_cam_orien[:,0], label='v cam_orien_x')
plt.xlabel("frame no")
plt.ylabel("cam_orien x(pitch) in rad)")
plt.title("cam x(pitch) orientation")
plt.legend()

if debug_param.show_plot:
    plt.show(block=False)
    plt.pause(0.1)

plt.savefig("%s/cam_orien_x.png"%result_dir)
plt.close(fig)


fig = plt.figure(figsize=(20, 10))
plt.plot(p_cam_orien[:,1], label='p_cam_orien_y')
plt.plot(v_cam_orien[:,1], label='v cam_orien_y')
plt.xlabel("frame no")
plt.ylabel("cam_orien y(yaw) in rad)")
plt.title("cam y(yaw) orientation")
plt.legend()
plt.savefig("%s/cam_orien_y.png"%result_dir)
if debug_param.show_plot:
    plt.show(block=False)
    plt.pause(0.1)
plt.close(fig)

fig = plt.figure(figsize=(20, 10))
plt.plot(p_cam_orien[:,2], label='p_cam_orien_z')
plt.plot(v_cam_orien[:,2], label='v cam_orien_z')
plt.xlabel("frame no")
plt.ylabel("cam_orien z(roll) in rad)")
plt.title("cam z(roll) orientation")
plt.legend()
plt.savefig("%s/cam_orien_z.png"%result_dir)
if debug_param.show_plot:
    plt.show(block=False)
    plt.pause(0.1)
plt.close(fig)

fig = plt.figure(figsize=(20, 10))
plt.subplot(3,1,1)
plt.plot(alpha[eis_param.lookahead_no:],color='g',label='alpha')
plt.legend()
plt.subplot(3,1,2)
plt.plot(uncompensated_dist[eis_param.lookahead_no:],label='uncompenstated_dist')
plt.legend()
plt.subplot(3,1,3)
plt.plot(out_of_boundary[eis_param.lookahead_no:],color='r',label='is_out_of_boundary')
plt.ylim(-0.5,1.5)
plt.legend()
plt.savefig("%s/boundary_control.png"%result_dir)
if debug_param.show_plot:
    plt.show(block=False)
    plt.pause(0.1)
plt.close(fig)

fig = plt.figure(figsize=(20, 20))
plt.subplot(5,1,1)
plt.plot(p_cam_orien[eis_param.lookahead_no:,0], label='p_cam_orien_x')
plt.plot(v_cam_orien[eis_param.lookahead_no:,0], label='v cam_orien_x')
plt.xlabel("frame no")
plt.ylabel("cam_orien x(pitch) in rad)")
plt.title("cam x(pitch) orientation")
plt.legend()
plt.subplot(5,1,2)
plt.plot(p_cam_orien[eis_param.lookahead_no:,1], label='p_cam_orien_y')
plt.plot(v_cam_orien[eis_param.lookahead_no:,1], label='v cam_orien_y')
plt.xlabel("frame no")
plt.ylabel("cam_orien y(yaw) in rad)")
plt.title("cam y(yaw) orientation")
plt.legend()
plt.subplot(5,1,3)
plt.plot(p_cam_orien[eis_param.lookahead_no:,2], label='p_cam_orien_z')
plt.plot(v_cam_orien[eis_param.lookahead_no:,2], label='v cam_orien_z')
plt.xlabel("frame no")
plt.ylabel("cam_orien z(roll) in rad)")
plt.title("cam z(roll) orientation")
plt.legend()
plt.subplot(5,1,4)
plt.plot(out_of_boundary[eis_param.lookahead_no:],color='r',label='is_out_of_boundary')
plt.ylim(-0.5,1.5)
plt.legend()
plt.subplot(5,1,5)
plt.plot(alpha[eis_param.lookahead_no:],color='g',label='alpha')
plt.legend()
plt.savefig("%s/path_analysis.png"%result_dir)
if debug_param.show_plot:
    plt.show(block=False)
    plt.pause(0.1)
plt.close(fig)

if OOB_ON:
    # load video
    video_ext_path = result_dir + '/compare_*.mp4'
    video_filename = glob.glob(video_ext_path)[0].split('/')[-1]
    in_compare_video_path = result_dir +'/'+ video_filename
    out_compare_video_path = result_dir +'/'+ video_filename.split('.')[0]  + '_oob.mp4'

    # read video
    video = cv2.VideoCapture(in_compare_video_path)
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_rate  = int(video.get(cv2.CAP_PROP_FPS))
    # write video
    out_video = cv2.VideoWriter(out_compare_video_path, cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, (frame_width, frame_height))
    #result log path
    result_image_dir = result_dir + '/image'

    if not os.path.exists(result_image_dir):
        os.makedirs(result_image_dir)

    crop_ratio = eis_param.crop_ratio

    warp_width = int(0.5*frame_width)
    warp_height = int(frame_height)
    crop_roi_x1 = int(0.5*frame_width+crop_ratio * warp_width)
    crop_roi_x2 = int(0.5*frame_width+(1.0 - crop_ratio) * warp_width)
    crop_roi_y1 = int(crop_ratio * warp_height)
    crop_roi_y2 = int((1.0 - crop_ratio) * warp_height)

    frame_count = 0
        
    while True:
        
        ret, frame = video.read()
        if not ret:
            break
        print("========================================")
        print("frame_count = %d"%frame_count)            
        


        # print log on screen
        if out_of_boundary[frame_count]:
            oob_text = 'oob'
            cv2.putText(frame, oob_text, (int(10+frame_width*0.5), 40), cv2.FONT_HERSHEY_SIMPLEX,2, (0, 0, 255), 2, cv2.LINE_AA)
        
        uncomp_text = '%.2f'%uncompensated_dist[frame_count]
        cv2.putText(frame, 'uncomp_dist', (int(400+frame_width*0.5), 40), cv2.FONT_HERSHEY_SIMPLEX,2, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, uncomp_text, (int(400+frame_width*0.5), 140), cv2.FONT_HERSHEY_SIMPLEX,2, (255, 0, 0), 2, cv2.LINE_AA)
        
        alpha_text = '%.2f'%alpha[frame_count]
        cv2.putText(frame, 'alpha', (int(1000 +frame_width*0.5), 40), cv2.FONT_HERSHEY_SIMPLEX,2, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, alpha_text, (int(1000+frame_width*0.5), 140), cv2.FONT_HERSHEY_SIMPLEX,2, (255, 0, 0), 2, cv2.LINE_AA)

        cv2.rectangle(frame, (crop_roi_x1, crop_roi_y1), (crop_roi_x2, crop_roi_y2), (0, 255, 0), 2)
        
        out_video.write(frame)
        if debug_param.log_image:
            image_path =result_image_dir + '/frame_%05d.jpg'%frame_count
            cv2.imwrite(image_path,frame)

        frame_count+=1


    video.release()
    out_video.release()

os.system('rm -rf eis_core')
os.system('rm config_path.py')