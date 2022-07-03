import ipdb
import sys
import json
import numpy as np
import time
import cv2
import os
import glob
import config_path
import threading
from collections import deque
from sig_gen import sig_gen
from eis_core import eis_core_config_loader
from eis_core import eis_core_queue_handler
from eis_core import eis_core_pass1
from eis_core import eis_core_pass2

if len(sys.argv)!=2:
    print("Please enter: run_video_stab.py log_dir")
    exit()
else:
    log_dir = sys.argv[1]

# load eis log
video_meta_log_path = log_dir + '/cs.log'
gyro_log_path = log_dir + '/imu.log'

# load video
video_ext_path = log_dir + '/*.mp4'
video_filename = glob.glob(video_ext_path)[0].split('/')[-1]
video_path = log_dir + '/' + video_filename

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

trans_matrix_path = result_dir + '/trans_matrix.log'
mesh_grid_x_path = result_dir + '/mesh_grid_x.log'
mesh_grid_y_path = result_dir + '/mesh_grid_y.log'
#============================ run  eis pass 1 =========================================

if debug_param.eis_pass1:

    # read video
    video = cv2.VideoCapture(video_path)

    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_rate  = int(video.get(cv2.CAP_PROP_FPS)+0.5)
    
    # load video param
    video_param = eis_core_config_loader.load_video_config(config_path.video_config_path,frame_width,frame_height,frame_rate)

    f_t = open(trans_matrix_path, 'w')
    f_x = open(mesh_grid_x_path, 'w')
    f_y = open(mesh_grid_y_path, 'w')

    # eis pass 1 initialize
    eis_pass1 = eis_core_pass1.EIS_PASS1(video_param)

    # create gyro buffer
    gyro_buffer = eis_core_queue_handler.EISGyroQueue(frame_rate)

    # the condition of cmos signal 
    frame_signal_cond = threading.Condition()

    # initialize eis signal 
    eis_signal = sig_gen.EIS_SIGNAL(video_meta_log_path, gyro_log_path,gyro_buffer,0.0,frame_signal_cond)

    prev_vsync_ts = 0

    # start eis signal 
    eis_signal.start()
    
    frame_count = 0
    
    while eis_signal.activate:
        
        
        if len(eis_signal.cmos_sig)>0:
            
            frame_signal_cond.acquire()
            
            vsync_ts , exptime = eis_signal.cmos_sig
            
            frame_signal_cond.wait()
            frame_signal_cond.release()
            
            # this is to prevent droping frames, so we interrupt every vsync_duration, while drop frames situation happen in video log, 
            # it can be distinguish  by prevouse vsync timestap
            if vsync_ts != prev_vsync_ts:

                print("=============================================================")
                print("frame_count = %d"%frame_count)
                print("start of frame: vs = %d, exp = %d"%(vsync_ts, exptime))
                
                # TODO: move to eis program
                last_gyro_ts = gyro_buffer[-1][0]
                
                eis_pass1.wait_for_frame_generation(vsync_ts/10**eis_signal.cmos_exp, exptime/10**eis_signal.cmos_exp, last_gyro_ts)
                
                # print("[gyro buffer snapshot]:")
                # print("----------------------------------------------------------")
                # buffer_len = gyro_buffer.size()
                # for i in range(buffer_len):
                #     ts, gx, gy, gz = gyro_buffer[buffer_len-i-1]
                #     print("ts = %f, gx = %f, gy = %f, gz = %f"%(ts, gx, gy, gz))
                # print("----------------------------------------------------------")

                if frame_count > debug_param.start_frame_no:                
                    slice_trans_matrix,mesh_grid_x, mesh_grid_y = eis_pass1.run(vsync_ts/10**eis_signal.cmos_exp, exptime/10**eis_signal.cmos_exp, gyro_buffer)
                    
                    for i in range(len(slice_trans_matrix)):
                        
                        f_t.write('%.15f %.15f %.15f %.15f %.15f %.15f %.15f %.15f %.15f ' %
                            (slice_trans_matrix[i][0][0], slice_trans_matrix[i][0][1], slice_trans_matrix[i][0][2],
                            slice_trans_matrix[i][1][0], slice_trans_matrix[i][1][1], slice_trans_matrix[i][1][2], 
                            slice_trans_matrix[i][2][0], slice_trans_matrix[i][2][1], slice_trans_matrix[i][2][2]))

                        if i == len(slice_trans_matrix)-1:
                            f_t.write('\n')
                    
                    grid_size = len(mesh_grid_x)
                    print("grid_size = %d"%grid_size)

                    for i in range(grid_size):
                        for j in range(grid_size):
                            f_x.write('%.4f '%mesh_grid_x[i,j])
                    f_x.write('\n')

                    for i in range(grid_size):
                        for j in range(grid_size):
                            f_y.write('%.4f '%mesh_grid_y[i,j])
                    f_y.write('\n')

                        

                prev_vsync_ts = vsync_ts

                frame_count+=1

        if not eis_signal.activate:
            break
        

    # end of eis signal thread
    eis_signal.join()
    f_t.close()
    f_x.close()
    f_y.close()
    video.release()

    

#============================ run  eis pass 2 =========================================

if debug_param.eis_pass2:
    
    

    if debug_param.use_opengl:
        ######################################################
        #               use opengl warp                      #
        # ####################################################

        os.chdir("../c")
        os.system("make clean")
        os.system("make")
        cmd_str = "./run_eis " + log_dir
        os.system(cmd_str)
    

    else:

        #########################################################
        #               use python cv warp                      #
        # #######################################################

        #result log path
        result_image_dir = result_dir + '/image'

        if not os.path.exists(result_image_dir):
            os.makedirs(result_image_dir)

        print("run eis pass2!")
        # read video
        video = cv2.VideoCapture(video_path)

        frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_rate  = int(video.get(cv2.CAP_PROP_FPS))
        # load video param
        video_param = eis_core_config_loader.load_video_config(config_path.video_config_path,frame_width,frame_height,frame_rate)

        eis_pass2 = eis_core_pass2.EIS_PASS2(video_param)

        if debug_param.preserve_margin:
            out_frame_height = eis_pass2.warp_height
            out_frame_width = eis_pass2.warp_width
        else:
            out_frame_height = frame_height
            out_frame_width = frame_width

        out_vid_name = video_filename.split('.')[0] 
    
        stable_video_path = '%s/stable_%s.mp4'%(result_dir,out_vid_name)
        stable_videoWriter = cv2.VideoWriter(stable_video_path, cv2.VideoWriter_fourcc(*'mp4v'), video_param.frame_rate, (out_frame_width, out_frame_height))

        compare_video_path = '%s/compare_%s.mp4'%(result_dir,out_vid_name)
        comp_videoWriter = cv2.VideoWriter(compare_video_path, cv2.VideoWriter_fourcc(*'mp4v'), video_param.frame_rate, (out_frame_width * 2, out_frame_height))

        f_t = open(trans_matrix_path, 'r')
        
        frame_count = 0
        total_warp_duration = 0
        while True:
            
            ret, frame = video.read()
            if not ret:
                break
            print("========================================")
            print("frame_count = %d"%frame_count)        
            
            if frame_count > debug_param.start_frame_no:
                line = f_t.readline()

                if not line:
                    break
                slice_trans_matrices = np.array((line.rstrip()).split(' ')).astype(np.float).reshape((eis_pass2.num_of_slice+1,3,3))
                
                start_time = time.time()
                
                stable_frame = eis_pass2.run(frame, slice_trans_matrices)

                end_time = time.time()

                total_warp_duration  += end_time -start_time

                stable_videoWriter.write(stable_frame)
                
                if eis_pass2.lookahead_no > 0:
                    scaleup_frame = cv2.resize(eis_pass2.forward_frame, (eis_pass2.warp_width, eis_pass2.warp_height), interpolation=cv2.INTER_CUBIC)
                else:
                    scaleup_frame = cv2.resize(frame, (eis_pass2.warp_width, eis_pass2.warp_height), interpolation=cv2.INTER_CUBIC)
                    
            
                if debug_param.preserve_margin:
                    origin_crop_frame = scaleup_frame
                else:
                    origin_crop_frame = scaleup_frame[eis_pass2.crop_roi_y1:eis_pass2.crop_roi_y2, eis_pass2.crop_roi_x1:eis_pass2.crop_roi_x2:]
                
                compare_frame = np.concatenate((origin_crop_frame, stable_frame), axis=1)
                comp_videoWriter.write(compare_frame)
            
                if debug_param.log_image:
                    image_path =result_image_dir + '/frame_%03d.jpg'%frame_count
                    cv2.imwrite(image_path,compare_frame)

                    # image_path =result_image_dir + '/frame_stable%03d.jpg'%frame_count
                    # cv2.imwrite(image_path,stable_frame)
            
            frame_count+=1


                
        f_t.close()
        video.release()    
        comp_videoWriter.release()
        stable_videoWriter.release()

        print('eis_pass2 execution time: %f, average warp per frame = %f'%((total_warp_duration),(total_warp_duration)/frame_count))

