import cv2
import numpy as np
import ipdb
import config_path
from eis_core import eis_core_config_loader
from eis_core import eis_core_queue_handler
from collections import deque

class EIS_PASS2(object):

    def __init__(self,video_param):

        # laoding config
        eis_param = eis_core_config_loader.load_eis_config(config_path.eis_config_path)
        debug_param = eis_core_config_loader.load_debug_config(config_path.debug_config_path)
        self.warp_with_resize = debug_param.warp_with_resize
        self.preserve_margin = debug_param.preserve_margin
        self.num_of_slice = eis_param.knee_point +1
        self.scale_ratio  = 1.0 / (1 - eis_param.crop_ratio * 2)
        self.frame_width = video_param.frame_width
        self.frame_height = video_param.frame_height
        self.warp_width = int(video_param.frame_width * self.scale_ratio)
        self.warp_height = int(video_param.frame_height * self.scale_ratio)
        self.crop_roi_x1 = int(eis_param.crop_ratio * self.warp_width)
        self.crop_roi_x2 = self.crop_roi_x1 + video_param.frame_width #int((1.0 - eis_param.crop_ratio) * self.warp_width)
        self.crop_roi_y1 = int(eis_param.crop_ratio * self.warp_height)
        self.crop_roi_y2 = self.crop_roi_y1 + video_param.frame_height#int((1.0 - eis_param.crop_ratio) * self.warp_height)
        # frame buffer for look ahead low-pass filter 
        self.lookahead_no = eis_param.lookahead_no
        self.frame_buffer = eis_core_queue_handler.RingBuffer(self.lookahead_no)
        self.forward_frame = np.zeros((video_param.frame_height, video_param.frame_width, 3), np.uint8)
        self.scale_matrix = np.array([[1.0 / self.scale_ratio, 0, 0], [0, 1.0 / self.scale_ratio, 0], [0, 0, 1]]).astype(float)


    def create_slice_coord_map(self,trans_matrices, w, h):
        
        indy, indx = np.indices((h, w), dtype=np.float32)
        
        slice_h = h/self.num_of_slice
        map_x = np.zeros((h,w),dtype=np.float32)
        map_y = np.zeros((h,w),dtype=np.float32)
        
        y1 = 0
        for i in range(self.num_of_slice):

            x0 = 0
            x1 = w
            y0 = y1 
            y1 = y0 + int(slice_h)
            y1 = min(y1,h)
            s_h = y1 -y0
            
            slice_indy = indy[y0:y1,x0:x1]
            slice_indx = indx[y0:y1,x0:x1]
            lin_homg_ind = np.array([slice_indx.ravel(), slice_indy.ravel(), np.ones_like(slice_indx).ravel()])
            trans_matrix = trans_matrices[i+1]
            if self.warp_with_resize:
                trans_matrix = np.dot(trans_matrix,self.scale_matrix)
            
            # warp the coordinates of src to those of true_dst
            slice_map_ind = trans_matrix.dot(lin_homg_ind)
            slice_map_x, slice_map_y = slice_map_ind[:-1] / slice_map_ind[-1]  # ensure homogeneity
            slice_map_x = slice_map_x.reshape(s_h, w).astype(np.float32)
            slice_map_y = slice_map_y.reshape(s_h, w).astype(np.float32)
            map_x[y0:y1,x0:x1] = slice_map_x
            map_y[y0:y1,x0:x1] = slice_map_y


        return map_x, map_y

    def create_coord_map(self, trans_matrix, w, h):

        indy, indx = np.indices((h, w), dtype=np.float32)
        lin_homg_ind = np.array([indx.ravel(), indy.ravel(), np.ones_like(indx).ravel()])

        # warp the coordinates of src to those of true_dst
        map_ind = trans_matrix.dot(lin_homg_ind)
        map_x, map_y = map_ind[:-1] / map_ind[-1]  # ensure homogeneity
        map_x = map_x.reshape(h, w).astype(np.float32)
        map_y = map_y.reshape(h, w).astype(np.float32)


        return map_x, map_y

    def image_warp(self, frame, trans_matrices):

        
        if self.warp_with_resize:
            map_x, map_y = self.create_slice_coord_map(trans_matrices, self.warp_width, self.warp_height)
            warp_frame = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)

        else:
            map_x, map_y = self.create_slice_coord_map(trans_matrices, self.frame_width, self.frame_height)
            small_warp_frame = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)
            warp_frame = cv2.resize(small_warp_frame,(self.warp_width,self.warp_height),interpolation=cv2.INTER_CUBIC)
        
        # map_x, map_y = self.create_slice_coord_map(trans_matrix, self.warp_width, self.warp_height)
        # warp_frame = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)

        
        return warp_frame
    

    def image_warp_by_cv(self, frame, trans_matrix):

        inv_trans_matrix = np.linalg.inv(trans_matrix)

        return cv2.warpPerspective(frame, inv_trans_matrix, (self.warp_width, self.warp_height))

    def run(self,frame, trans_matrices):
        
        warp_frame = np.zeros((self.warp_height, self.warp_width, 3), np.uint8)
        
        if self.lookahead_no> 0:
            # apply FIR filter
            if len(self.frame_buffer.get()) >= self.lookahead_no:

                self.forward_frame = self.frame_buffer.get()[1].copy()
                warp_frame = self.image_warp(self.forward_frame, trans_matrices)
            
            self.frame_buffer.append(frame)
            
        else:
            # apply IIR filter
            warp_frame = self.image_warp(frame, trans_matrices)

      
        if self.preserve_margin:
            stable_frame = warp_frame
        else:
            stable_frame = warp_frame[self.crop_roi_y1:self.crop_roi_y2, self.crop_roi_x1:self.crop_roi_x2:]

            
        return stable_frame

        


