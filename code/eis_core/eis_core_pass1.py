import cv2
import numpy as np
import math
import time
import config_path
from eis_core import eis_core_quat
from eis_core import eis_core_config_loader
from scipy.spatial import distance
import ipdb
import matplotlib.pyplot as plt
from pyquaternion import Quaternion
from collections import deque
from numpy.linalg import inv

class EIS_PASS1(object):
    
    def __init__(self,video_param):

        # laoding config
        eis_param = eis_core_config_loader.load_eis_config(config_path.eis_config_path)
        cmos_param = eis_core_config_loader.load_cmos_config(config_path.cmos_config_path)
        debug_param = eis_core_config_loader.load_debug_config(config_path.debug_config_path)
        
        self.use_opengl = debug_param.use_opengl

        self.rs_correct_off = debug_param.rs_correct_off

        self.warp_with_resize = debug_param.warp_with_resize

        self.use_nonlinear_filter = eis_param.use_nonlinear_filter

        self.num_of_knee_pts = eis_param.knee_point
        
        self.num_of_slice = self.num_of_knee_pts + 1

        self.frame_rate = video_param.frame_rate

        self.frame_duration = 1.0/video_param.frame_rate
        
        self.cmos_frame_height = cmos_param.cmos_frame_height
        # besides non effective blanking image line, we supposed effective image in the moddile of frame
        
        self.top_blanking = int(0.5*(self.cmos_frame_height- cmos_param.effective_height))*(video_param.frame_height/cmos_param.effective_height)
    
        print('top blanking = %d'%self.top_blanking)
        
        #self.effective_height = int((self.cmos_frame_height - cmos_param.blanking)*(video_param.frame_height/cmos_param.effective_height))

        self.frame_height = video_param.frame_height

        self.frame_width = video_param.frame_width

        # the rs_time here is the duration from first to last line of a frame
        if self.frame_height/self.frame_width > 0.7:
            # 4:3 video ratio
            self.rs_time = self.frame_duration
        else:
            # 16:9 video ratio
            self.rs_time = self.frame_duration * (cmos_param.effective_height/cmos_param.cmos_frame_height)
        
        self.line_duration = self.rs_time/self.frame_height
        
        print('frame_rate = %f'%self.frame_rate)
        print('frame_duration = %f'%self.frame_duration)
        print('line_duration = %f'%self.line_duration)
        print('rs_time = %f'%self.rs_time)
        
        # TODO: change focal length by image size
        
        self.focal_in_pixel = (cmos_param.focal_in_mm/cmos_param.sensor_width_in_mm)*cmos_param.cmos_frame_width *(video_param.frame_height/cmos_param.effective_height)
        
        print("================================")
        print('focal length = %f'%self.focal_in_pixel)
        print("================================")
        
        # number of frame of look-ahead low-pass filter
        self.lookahead_no = eis_param.lookahead_no

        # non-linear filer stabilization algorithm parameters
        self.alpha = eis_param.alpha
        self.alpha_min = eis_param.alpha_min
        self.alpha_max = eis_param.alpha_max
        self.damping = eis_param.damping
        self.beta = eis_param.beta
        self.gamma = eis_param.gamma
        self.crop_roi = np.zeros((4, 2))
        self.inner_roi = np.zeros((4, 2))
        self.outer_roi = np.zeros((4, 2))

        # previous parameters
        self.prev_exptime = 0.0
        self.prev_vsync_ts = 0.0
        self.prev_v_cam_velocity = Quaternion()
        self.prev_p_cam_orien = Quaternion()
        self.prev_v_cam_orien = Quaternion()
        self.prev_pv_cam_velocity = Quaternion()
        
        # look-ahead buffer
        if self.lookahead_no > 0:
            self.p_cam_orien_buffer = deque(maxlen=self.lookahead_no)
            self.p_cam_velocity_buffer = deque(maxlen=self.lookahead_no)
            self.v_cam_orien_buffer = deque(maxlen=self.lookahead_no)
            self.v_cam_velocity_buffer = deque(maxlen=self.lookahead_no)
        
        crop_ratio = eis_param.crop_ratio
        scale_ratio = 1.0 / (1 - crop_ratio * 2)

        self.frame_width = video_param.frame_width
        self.frame_height = video_param.frame_height
        
        self.warp_width = int(self.frame_width * scale_ratio)
        self.warp_height = int(self.frame_height * scale_ratio)
    
        # inner/outer padding region ratio
        inner_padding_ratio = eis_param.inner_padding_ratio
        outer_padding_ratio = crop_ratio * (1 - inner_padding_ratio)

        outer_width = int(crop_ratio * self.frame_width)
        outer_height = int(crop_ratio * self.frame_height)
        self.outer_dist = outer_height#(outer_width**2 + outer_height**2)**0.5
        print('out_dist = %f'%self.outer_dist)
        # crop roi coordinate in warp frame resolusion,
        # we use the warp frame resolusion due to the trans_matrix include warp scale-up scale
        crop_roi_x1 = int(crop_ratio * self.frame_width)
        crop_roi_x2 = int((1.0 - crop_ratio) * self.frame_width)
        crop_roi_y1 = int(crop_ratio * self.frame_height)
        crop_roi_y2 = int((1.0 - crop_ratio) * self.frame_height)

        self.crop_roi[0, :] = [crop_roi_x1, crop_roi_y1]
        self.crop_roi[1, :] = [crop_roi_x2, crop_roi_y1]
        self.crop_roi[2, :] = [crop_roi_x2, crop_roi_y2]
        self.crop_roi[3, :] = [crop_roi_x1, crop_roi_y2]

        # calculate the range of inner region 
        inner_roi_x1 = int(outer_padding_ratio * self.frame_width)
        inner_roi_x2 = int((1.0 - outer_padding_ratio) * self.frame_width)
        inner_roi_y1 = int(outer_padding_ratio * self.frame_height)
        inner_roi_y2 = int((1.0 - outer_padding_ratio) * self.frame_height)

        self.inner_roi[0, :] = [inner_roi_x1, inner_roi_y1]
        self.inner_roi[1, :] = [inner_roi_x2, inner_roi_y1]
        self.inner_roi[2, :] = [inner_roi_x2, inner_roi_y2]
        self.inner_roi[3, :] = [inner_roi_x1, inner_roi_y2]

        #calculate the range of outer region
        outer_roi_x1 = 0
        outer_roi_x2 = self.frame_width - 1
        outer_roi_y1 = 0
        outer_roi_y2 = self.frame_height - 1

        self.outer_roi[0, :] = [outer_roi_x1, outer_roi_y1]
        self.outer_roi[1, :] = [outer_roi_x2, outer_roi_y1]
        self.outer_roi[2, :] = [outer_roi_x2, outer_roi_y2]
        self.outer_roi[3, :] = [outer_roi_x1, outer_roi_y2]

            
    def wait_for_frame_generation(self, vsync_ts, exptime, last_gyro_ts):

        last_line_exp_ts = vsync_ts + (self.top_blanking + self.frame_height)*self.line_duration - exptime*0.5#vsync_ts + self.frame_duration - 0.5*exptime
        
        if last_gyro_ts < last_line_exp_ts:
            
            wait_imu_data_in_sec =  last_line_exp_ts - last_gyro_ts
            #print("last_gyros < last line exp ts, wait imu_buffer %f sec.."%(wait_imu_data_in_sec))
            time.sleep(wait_imu_data_in_sec)
        
        
    def cal_inter_frame_duration(self, vsync_timestamp, exptime):
        
        if self.prev_exptime == 0.0:
            prev_exptime = exptime
        else:
            prev_exptime = self.prev_exptime

        if self.prev_vsync_ts == 0.0:

            prev_vsync_ts = vsync_timestamp - self.frame_duration
        else:
            prev_vsync_ts = self.prev_vsync_ts

        prevous_frame_ts = prev_vsync_ts + self.top_blanking*self.line_duration - prev_exptime*0.5 
        current_frame_ts = vsync_timestamp + self.top_blanking *self.line_duration - exptime*0.5 
        
        return prevous_frame_ts, current_frame_ts

    def cal_intra_frame_duration(self, vsync_timestamp, exptime):

        first_line_ts = vsync_timestamp + self.top_blanking*self.line_duration - exptime*0.5
        last_line_ts =  vsync_timestamp + (self.top_blanking + self.frame_height)*self.line_duration - exptime*0.5

        return first_line_ts, last_line_ts
    
    
    def extract_gyro_samples_from_buffer(self, gyro_buffer, start_timestamp, end_timestamp):
        
        gyro_samples = []
        buffer_size = len(gyro_buffer)
        idx = buffer_size

        # interpolate last gyro sample
        for i in reversed(range(buffer_size)):

            t1 =  gyro_buffer[i].ts
            gx1 = gyro_buffer[i].gx
            gy1 = gyro_buffer[i].gy
            gz1 = gyro_buffer[i].gz

            t0 =  gyro_buffer[i-1].ts
            gx0 = gyro_buffer[i-1].gx
            gy0 = gyro_buffer[i-1].gy
            gz0 = gyro_buffer[i-1].gz


            if t1 >= end_timestamp and end_timestamp >= t0:

                gx = np.interp(end_timestamp, [t0, t1], [gx0, gx1])
                gy = np.interp(end_timestamp, [t0, t1], [gy0, gy1])
                gz = np.interp(end_timestamp, [t0, t1], [gz0, gz1])
                
                # check the interpolation result
                # print("t0 =     %f, gx0 = %f, gy0 = %f, gz0 = %f"%(t0, gx0, gy0, gz0))
                # print("cur_ts = %f, gx  = %f, gy  = %f, gz  = %f"%(end_timestamp,gx, gy,gz))
                # print("t1 =     %f, gx1 = %f, gy1 = %f, gz1 = %f"%(t1, gx1, gy1, gz1))
                
                gyro_samples.append([end_timestamp, gx, gy, gz])
                
                # record the index 
                idx = i-1
                #print("stop to idx = %d"%idx)

                break
        
        for i in reversed(range(idx+1)):

            t =  gyro_buffer[i].ts
            gx = gyro_buffer[i].gx
            gy = gyro_buffer[i].gy
            gz = gyro_buffer[i].gz
            
            if t > start_timestamp:
                gyro_samples.append([t, gx, gy, gz])
            else: 
                idx = i
                #print("stop to idx = %d"%idx)
                break

        t1 =  gyro_buffer[i+1].ts
        gx1 = gyro_buffer[i+1].gx
        gy1 = gyro_buffer[i+1].gy
        gz1 = gyro_buffer[i+1].gz

        t0 =  gyro_buffer[i].ts
        gx0 = gyro_buffer[i].gx
        gy0 = gyro_buffer[i].gy
        gz0 = gyro_buffer[i].gz

        gx = np.interp(start_timestamp, [t0, t1], [gx0, gx1])
        gy = np.interp(start_timestamp, [t0, t1], [gy0, gy1])
        gz = np.interp(start_timestamp, [t0, t1], [gz0, gz1])

        # check the interpolation result
        #print("t0 =     %f, gx0 = %f, gy0 = %f, gz0 = %f"%(t0, gx0, gy0, gz0))
        #print("prev_ts= %f, gx  = %f, gy  = %f, gz  = %f"%(prev_frame_ts,gx, gy,gz))
        #print("t1 =     %f, gx1 = %f, gy1 = %f, gz1 = %f"%(t1, gx1, gy1, gz1))

        gyro_samples.append([start_timestamp, gx, gy, gz])

        
        return gyro_samples

    def cal_angular_from_angular_velocity(self,gyro_samples):

        anlgle_x = 0
        anlgle_y = 0
        anlgle_z = 0

        for i in range(len(gyro_samples)-1):
            
            t0, g0x, g0y, g0z = gyro_samples[i]
            t1, g1x, g1y, g1z = gyro_samples[i+1]
            
            dt = t0 - t1

            angular_velocity_x = (g0x + g1x) *0.5
            angular_velocity_y = (g0y + g1y) *0.5
            angular_velocity_z = (g0z + g1z) *0.5

            anlgle_x += angular_velocity_x * dt
            anlgle_y += angular_velocity_y * dt
            anlgle_z += angular_velocity_z * dt 


        return anlgle_x, anlgle_y, anlgle_z

    def extract_inter_frame_angluar_velocity(self, vsync_timestamp, exptime, gyro_buffer):
        
        prev_frame_ts, current_frame_ts = self.cal_inter_frame_duration(vsync_timestamp, exptime)

        print('prev_frame_ts = %f, current_frame_ts = %f, dt = %f'%(prev_frame_ts, current_frame_ts, current_frame_ts-prev_frame_ts))

        inter_frame_gyro_samples = self.extract_gyro_samples_from_buffer(gyro_buffer, prev_frame_ts, current_frame_ts)

        #check the inter-frame gyro data
        # print("\nframe samples:")
        # for i in range(len(inter_frame_gyro_samples)):
        #     print("ts = %f, gx = %f, gy = %f, gz = %f"
        #     %(inter_frame_gyro_samples[i][0],inter_frame_gyro_samples[i][1],inter_frame_gyro_samples[i][2],inter_frame_gyro_samples[i][3]))
        
        return inter_frame_gyro_samples
    
    def extract_intra_frame_angular_velocity(self, vsync_timestamp, exptime, gyro_buffer):

        first_line_ts, last_line_ts = self.cal_intra_frame_duration(vsync_timestamp, exptime)
        
        print('first_line_ts = %f, last_line_ts = %f'%(first_line_ts, last_line_ts))

        intra_frame_gyro_samples = self.extract_gyro_samples_from_buffer(gyro_buffer, first_line_ts, last_line_ts)

        return intra_frame_gyro_samples
        

    def cal_trans_polygon(self,trans_matrix,crop_polygon):

        trans_crop_polygon = np.zeros((4, 2))

        for i in range(4):
            index = np.array([crop_polygon[i, 0], crop_polygon[i, 1], 1])
            trans_index = trans_matrix.dot(index)
            
            coord_x = trans_index[0] / trans_index[2]
            coord_y = trans_index[1] / trans_index[2]

            trans_crop_polygon[i, 0] = coord_x
            trans_crop_polygon[i, 1] = coord_y

        return trans_crop_polygon

    def cal_uncompensated_distance(self,frame_polygon):
        
        
        # for calculate 4 edge of frame_polygon, which order is:
        # p0 -----------p1
        # |              |
        # |              |
        # p3------------p2

        # find the minimun distance between crop roi vertex and the boundary of frame polygon
        uncompensated_dist = 9999

        for i in range(4):

            pts = self.crop_roi[i,:]
            m = pts[0]
            n = pts[1]
                
            for j in [-1,1]:
                
                i_adj = i+j
                if i_adj > 3:
                    i_adj = 0
                
                if i_adj < 0:
                    i_adj = 3

                p1 = frame_polygon[i,:]
                p2 = frame_polygon[i_adj,:]
                
                # equation of the edge of frame polygon: y = kx + d
                if p2[0]==p1[0]:
                    k = 0
                else:
                    k = (p2[1] - p1[1])/(p2[0] - p1[0])
                
                d = p1[1] - k*p1[0]
                dist = abs(k*m -n +d)/((k**2+1)**0.5)
                
                if dist < uncompensated_dist:
                    uncompensated_dist = dist
       

        return uncompensated_dist
            

    def is_out_crop_region(self, frame_polygon):
        
        uncompensated_dist = 9999
        is_in_frame_polygon = True
        
        for i in range(4):
            is_pts_in_frame_polygon = self.isPointinRect(self.crop_roi[i,0], self.crop_roi[i,1], frame_polygon)
            is_in_frame_polygon = is_in_frame_polygon and is_pts_in_frame_polygon
        
        uncompensated_dist = self.cal_uncompensated_distance(frame_polygon)
        
        if is_in_frame_polygon:
            return False, uncompensated_dist
        else:
            uncompensated_dist = 0
            return True, uncompensated_dist


    def isPointinRect(self,x, y, rectRegion):
        # pb---pc
        # |    |
        # pa---pd

        rect_pb_x = rectRegion[0, 0]
        rect_pb_y = rectRegion[0, 1]
        rect_pc_x = rectRegion[1, 0]
        rect_pc_y = rectRegion[1, 1]
        rect_pd_x = rectRegion[2, 0]
        rect_pd_y = rectRegion[2, 1]
        rect_pa_x = rectRegion[3, 0]
        rect_pa_y = rectRegion[3, 1]

        # line a from p1 to p2
        a = (rect_pb_x - rect_pa_x) * (y - rect_pa_y) - (rect_pb_y - rect_pa_y) * (x - rect_pa_x)

        # line a from p2 to p3
        b = (rect_pc_x - rect_pb_x) * (y - rect_pb_y) - (rect_pc_y - rect_pb_y) * (x - rect_pb_x)

        # line a from p3 to p4
        c = (rect_pd_x - rect_pc_x) * (y - rect_pc_y) - (rect_pd_y - rect_pc_y) * (x - rect_pc_x)

        # line a from p4 to p1
        d = (rect_pa_x - rect_pd_x) * (y - rect_pd_y) - (rect_pa_y - rect_pd_y) * (x - rect_pd_x)

        if (a > 0 and b > 0 and c > 0 and d > 0) or (a < 0 and b < 0 and c < 0 and d < 0):
            return True

        return False

    def is_inner_region(self, crop_polygon):

        is_in_inner_region = True
        
        #max_protrusion = 0
        for i in range(4):
            is_pts_in_inner_roi = self.isPointinRect(crop_polygon[i,0], crop_polygon[i,1], self.inner_roi)
            is_in_inner_region = is_in_inner_region and is_pts_in_inner_roi
           

        return is_in_inner_region


    def cal_trans_matrix(self,quat_p, quat_v):
        
        w = self.frame_width
        h = self.frame_height
        f = self.focal_in_pixel
        
        # Projection 2D -> 3D matrix
        invK = np.array([[1, 0, -w / 2], [0, 1, -h / 2], [0, 0, f]]).astype(float)
        K = np.linalg.inv(invK)
        #S = np.array([[1.0 / fx, 0, 0], [0, 1.0 / fy, 0], [0, 0, 1]]).astype(float)
        
        # Composed rotation matrix with quaternion
        # we use inverse interpolation to warp image, from stable to  unstable, x_v =  T * x_p
        # so, the sequence is to inverse phsycal camera orientation then rotate with virtual camera orientation
        
        quat_vp = quat_p.inverse*quat_v
        R = quat_vp.rotation_matrix

        # Final transformation matrix
        return np.dot(np.dot(K,R),invK)
        #return np.dot(np.dot(np.dot(K,R),invK),S)

    def integrate_inter_frame_orien(self, gyro_samples):

        p_cam_inter_frame_orien = Quaternion(self.prev_p_cam_orien)

        for i in range(len(gyro_samples)-1):
            t0, gx0, gy0, gz0 = gyro_samples[len(gyro_samples)-i-2]
            t1, gx1, gy1, gz1 = gyro_samples[len(gyro_samples)-i-1]
            dt = t0 -t1
            gx = (gx0+ gx1)*0.5
            gy = (gy0+ gy1)*0.5
            gz = (gz0+ gz1)*0.5
            
            p_cam_inter_frame_orien.integrate([gx,gy,gz],dt)
        
        return Quaternion(p_cam_inter_frame_orien)

    def integrate_intra_frame_orien_knee_pts(self, gyro_samples,cam_orien):   
        
       frame_cam_orien = Quaternion(cam_orien)
       frame_cam_orien_in_samples = []
       t1, gx1, gy1, gz1 = gyro_samples[-1]
       # append first line camera orientation
        
       frame_cam_orien_in_samples.append([t1,Quaternion(frame_cam_orien)])
       #integrate camera orientation in each gyro samples
       for i in range(len(gyro_samples)-1):
           t0, gx0, gy0, gz0 = gyro_samples[len(gyro_samples)-i-2]
           t1, gx1, gy1, gz1 = gyro_samples[len(gyro_samples)-i-1]
           dt = t0 -t1
           gx = (gx0+ gx1)*0.5
           gy = (gy0+ gy1)*0.5
           gz = (gz0+ gz1)*0.5
           frame_cam_orien.integrate([gx,gy,gz],dt)
           frame_cam_orien_in_samples.append([t0,Quaternion(frame_cam_orien)])

       #interpolation camera orientation in each knee points
       cam_orien_in_knee_pts = []
       t_start = gyro_samples[-1][0]
       t_end = gyro_samples[0][0]
       dt = (t_end - t_start)/self.num_of_slice
       
       for i in range(self.num_of_slice+1):
           t = t_start + i*dt
           for i in range(len(gyro_samples)-1):
               t0, q0 = frame_cam_orien_in_samples[i]
               t1, q1 = frame_cam_orien_in_samples[i+1]
               if t >= t0 and t <= t1:
                   s_r = (t-t0) /(t1-t0)
                   q_interp = Quaternion.slerp(q0,q1,s_r)
                   cam_orien_in_knee_pts.append(Quaternion(q_interp))
                   
                   break
    
       return cam_orien_in_knee_pts
    


    def cal_mesh_grid(self,trans_matrices,direction):
        
        grid_size = len(trans_matrices)
        mesh_grid_x = np.zeros((grid_size,grid_size))
        mesh_grid_y = np.zeros((grid_size,grid_size))
        
        if self.warp_with_resize:
            x_interv = int(self.warp_width/self.num_of_slice)
            y_interv = int(self.warp_height/self.num_of_slice)
        else:
            x_interv = int(self.frame_width/self.num_of_slice)
            y_interv = int(self.frame_height/self.num_of_slice)


        if direction == 0:
            refine_trans_matrices = []
            for i in range(len(trans_matrices)):
                refine_trans_matrices.append(inv(trans_matrices[i]))
        else:
            refine_trans_matrices = trans_matrices

        for i in range(grid_size):
            trans_matrix = refine_trans_matrices[i]
            for j in range(grid_size):
                idx_x = j*x_interv
                idx_y = i*y_interv
                homog_idx = np.array([idx_x,idx_y,1])
                grid_idx_xyz = trans_matrix.dot(homog_idx)
                
                grid_x = grid_idx_xyz[0]/grid_idx_xyz[2]
                grid_y = grid_idx_xyz[1]/grid_idx_xyz[2]
                mesh_grid_y[i,j] = grid_y
                mesh_grid_x[i,j] = grid_x

        return mesh_grid_x, mesh_grid_y


    def cal_slice_trans_matrix(self,knee_pts_quat_p, quat_v):

        # the knee points in the slice rectengle
        
        #  p00----------------p01
        #   |                 |    
        #  p10----------------p11
        #   |                 |    
        #  p20----------------p21
        #   .                 .
        #   .                 .
        #  pn0----------------pn1
        
        slice_trans_matrices = []

        for i in range(self.num_of_slice+1):
            # calculte transform matrix in knee points from p00 to pn0
            quat_p = Quaternion(knee_pts_quat_p[i])
            trans_matrix = self.cal_trans_matrix(quat_p,quat_v)
            slice_trans_matrices.append(trans_matrix)

        return slice_trans_matrices


    def cal_v_cam_velocity(self,p_cam_orien):
        
        prev_p_cam_velocity = (self.prev_p_cam_orien.conjugate*p_cam_orien).normalised
        v_cam_velocity = Quaternion.slerp(prev_p_cam_velocity,self.prev_v_cam_velocity,self.alpha)

        return v_cam_velocity


    def integrate_p_cam_orientation(self,vsync_timestamp,exptime, gyro_buffer):
        
        gyro_buffer_snapshot = gyro_buffer.copy()
        
        # extract inter-frame gyro samples
        inter_frame_gyro_samples = self.extract_inter_frame_angluar_velocity(vsync_timestamp, exptime, gyro_buffer_snapshot)
        
        # extract intra-frame gyro samples
        intra_frame_gyro_samples = self.extract_intra_frame_angular_velocity(vsync_timestamp, exptime, gyro_buffer_snapshot)

        #calculate inter-frame physical camera orientaion
        p_cam_inter_frame_orien = self.integrate_inter_frame_orien(inter_frame_gyro_samples)
        
        # append intra-frame phyiscal camera orientation
        p_cam_intra_frame_orien = self.integrate_intra_frame_orien_knee_pts(intra_frame_gyro_samples,p_cam_inter_frame_orien)

        #return Quaternion(p_cam_inter_frame_orien), p_cam_intra_frame_orien
        return p_cam_intra_frame_orien

    def update_filter(self,is_out_of_boundary, trans_matrix,uncompensated_dist):
       
        v_cam_velocity = Quaternion()
        is_in_inner_region = False

        if self.use_nonlinear_filter:

            # calculate transformation crop polygon
            crop_polygon = self.cal_trans_polygon(trans_matrix,self.crop_roi)

            is_in_inner_region = self.is_inner_region(crop_polygon)

            if is_in_inner_region:

                print('now is inner static region')
                v_cam_velocity = Quaternion.slerp(Quaternion(),self.prev_v_cam_velocity,self.damping)

            else:

                print('now is outer moving region')
                # with large max_margin_scale with smoother lpf
                alpha_ratio = (uncompensated_dist/(self.outer_dist))**self.beta
                alpha_ratio = max(alpha_ratio,0)
                alpha_ratio = min(alpha_ratio,1)
                alpha = alpha_ratio*self.alpha_max + (1-alpha_ratio)*self.alpha_min
                
                self.alpha  = 0.95*self.alpha + 0.05*alpha


        return is_in_inner_region, v_cam_velocity


    def boundary_detection(self, trans_matrices):

        frame_polygon = np.zeros((4, 2))
        for i in range(2):

            if i == 0:
                trans_matrix = np.linalg.inv(trans_matrices[0])
            else:
                trans_matrix = np.linalg.inv(trans_matrices[-1])
            
            for j in range(2):
                index = np.array([self.outer_roi[i*2+j, 0], self.outer_roi[i*2+j, 1], 1])
                trans_index = trans_matrix.dot(index)
                coord_x = trans_index[0] / trans_index[2]
                coord_y = trans_index[1] / trans_index[2]
                frame_polygon[i*2+j, 0] = coord_x
                frame_polygon[i*2+j, 1] = coord_y
               
        is_out_region, uncompensated_dist = self.is_out_crop_region(frame_polygon)

        return is_out_region, uncompensated_dist

    def boundary_conrtrol(self,p_cam_orien,pv_cam_velocity):
        
        v_cam_orien = (p_cam_orien[0]*pv_cam_velocity).normalised
        trans_matrices = self.cal_slice_trans_matrix(p_cam_orien, v_cam_orien)
        
        return v_cam_orien, trans_matrices   
    

    def run(self, vsync_timestamp, exptime, gyro_buffer):
        
        trans_matrices = []

        # integrate physical camera orientation
        p_cam_orien  = self.integrate_p_cam_orientation(vsync_timestamp,exptime, gyro_buffer)
        
        # integrate virtual camera oreintation in current frame
        v_cam_orien = (self.prev_v_cam_orien*self.prev_v_cam_velocity).normalised

        # low-pass filter for the current smooth virtual camera velocity
        v_cam_velocity = self.cal_v_cam_velocity(p_cam_orien[0])
        
        # calculate transformation matrix
        if self.lookahead_no > 0:
            
            if len(self.v_cam_velocity_buffer) >= self.lookahead_no:

                foward_v_cam_velocity = self.v_cam_velocity_buffer[0]
                for i in reversed(range(self.lookahead_no)):
                    foward_v_cam_velocity = Quaternion.slerp(self.p_cam_velocity_buffer[i],foward_v_cam_velocity,self.gamma)
                
                # virtual camera orientation integration
                self.v_cam_orien_buffer[1] = (self.v_cam_orien_buffer[0]* foward_v_cam_velocity).normalised
                forward_p_cam_orien = self.p_cam_orien_buffer[1]
                forward_v_cam_orien = self.v_cam_orien_buffer[1]
                trans_matrices = self.cal_slice_trans_matrix(forward_p_cam_orien,forward_v_cam_orien)
            else:
                
                for i in range(self.num_of_slice+1):
                    trans_matrix = self.cal_trans_matrix(Quaternion(),Quaternion())
                    trans_matrices.append(trans_matrix)

        else:

            # calculate transformation metrices in each knee points
            trans_matrices = self.cal_slice_trans_matrix(p_cam_orien, v_cam_orien)
       
        is_out_of_boudary,uncompensated_dist = self.boundary_detection(trans_matrices)
        
        if is_out_of_boudary:
            
            if self.lookahead_no > 0:
                pv_cam_velocity = (self.p_cam_orien_buffer[0][0].conjugate*self.v_cam_orien_buffer[0]).normalised
                self.v_cam_orien_buffer[1], trans_matrices = self.boundary_conrtrol(self.p_cam_orien_buffer[1],pv_cam_velocity)    
                # no need to update...maybe...
                #self.v_cam_velocity_buffer[0] = self.v_cam_orien_buffer[1]*self.v_cam_orien_buffer[0].conjugate
            else:
                v_cam_orien, trans_matrices = self.boundary_conrtrol(p_cam_orien,self.prev_pv_cam_velocity)
        
        # update non-linear filter
        is_in_inner_region, inner_v_cam_velocity = self.update_filter(is_out_of_boudary,trans_matrices[0],uncompensated_dist)
        
        # if in the inner region update the virtual camera veclocity
        if is_in_inner_region:
            v_cam_velocity = Quaternion(inner_v_cam_velocity)

        if self.lookahead_no > 0:    
            # push to buffer    
            self.p_cam_orien_buffer.append(p_cam_orien)
            self.v_cam_orien_buffer.append(Quaternion(v_cam_orien))
            self.v_cam_velocity_buffer.append(Quaternion(v_cam_velocity))
            self.p_cam_velocity_buffer.append(Quaternion((self.prev_p_cam_orien.conjugate*p_cam_orien[0]).normalised))
     
        
        # store to previous data
        self.prev_exptime = exptime
        self.prev_vsync_ts = vsync_timestamp
        self.prev_p_cam_orien = Quaternion(p_cam_orien[0])
        self.prev_v_cam_orien = Quaternion(v_cam_orien)
        self.prev_v_cam_velocity = Quaternion(v_cam_velocity)
        self.prev_pv_cam_velocity = (p_cam_orien[0].conjugate*v_cam_orien).normalised
        self.prev_is_oob = is_out_of_boudary


        # print camera orienation in eular
        if self.lookahead_no > 0 :
            if len(self.p_cam_orien_buffer) >= self.lookahead_no:
                p_cam_orien_x,p_cam_orien_y,p_cam_orien_z, = eis_core_quat.quaternion_to_euler_angle(self.p_cam_orien_buffer[0][0])
                v_cam_orien_x,v_cam_orien_y,v_cam_orien_z, = eis_core_quat.quaternion_to_euler_angle(self.v_cam_orien_buffer[0])
                print('v_cam_orientation x/y/z: %f, %f, %f'%(v_cam_orien_x,v_cam_orien_y, v_cam_orien_z))
                print('p_cam_orientation x/y/z: %f, %f, %f'%(p_cam_orien_x,p_cam_orien_y, p_cam_orien_z))
                print('is_out_of_boundary = %d'%is_out_of_boudary)
                print('uncompensated_dist = %f'%uncompensated_dist)
                print("alpha = %f"%self.alpha)
            else:
                print('v_cam_orientation x/y/z: %f, %f, %f'%(0.0,0.0, 0.0))
                print('p_cam_orientation x/y/z: %f, %f, %f'%(0.0,0.0, 0.0))
                print('is_out_of_boundary = %d'%(0))
                print('uncompensated_dist = %f'%(0))
                print("alpha = %f"%(0))
                
        else:
            p_cam_orien_x,p_cam_orien_y,p_cam_orien_z, = eis_core_quat.quaternion_to_euler_angle(self.prev_p_cam_orien)
            v_cam_orien_x,v_cam_orien_y,v_cam_orien_z, = eis_core_quat.quaternion_to_euler_angle(self.prev_v_cam_orien)
            print('v_cam_orientation x/y/z: %f, %f, %f'%(v_cam_orien_x,v_cam_orien_y, v_cam_orien_z))
            print('p_cam_orientation x/y/z: %f, %f, %f'%(p_cam_orien_x,p_cam_orien_y, p_cam_orien_z))
            print('is_out_of_boundary = %d'%is_out_of_boudary)
            print('uncompensated_dist = %f'%uncompensated_dist)
            print("alpha = %f"%self.alpha)
        
        mesh_grid_x, mesh_grid_y = self.cal_mesh_grid(trans_matrices,0)
        
        return trans_matrices,mesh_grid_x, mesh_grid_y
    

    def run_compensate_all(self, vsync_timestamp, exptime, gyro_buffer):

        # integrate physical camera orientation
        p_cam_orien  = self.integrate_p_cam_orientation(vsync_timestamp,exptime, gyro_buffer)
        
        #calculate virtual camera orientaion
        v_cam_orien = Quaternion(self.prev_v_cam_orien)

        if self.rs_correct_off:
            trans_matrices = []
            p_cam_orien = self.cal_trans_matrix(p_cam_orien[0],v_cam_orien)
            
            for i in range(self.num_of_slices):
                trans_matrices.append(p_cam_orien)

        else:

            trans_matrices = self.cal_slice_trans_matrix(p_cam_orien, v_cam_orien)

        self.prev_exptime = exptime
        self.prev_vsync_ts = vsync_timestamp
        self.prev_p_cam_orien = Quaternion(p_cam_orien[0])
        self.prev_v_cam_orien = Quaternion(v_cam_orien)
        
        return trans_matrices


   