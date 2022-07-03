 # # create slice coordinate
        # # the 4 points in the slice0 rectengle
        # #  p00----------------p01
        # #   |                  |    
        # #  p03----------------p02
        
        # slice_h = int(self.frame_height/self.num_of_slice)
        # self.slice_coord = np.zeros((self.num_of_slice,4,2),dtype= "float32")
        
        # for i in range(self.num_of_slice):
            
        #     self.slice_coord[i][0][0] = 0                       # pt0 x coordinate
        #     self.slice_coord[i][0][1] = 0 +  i * slice_h     # pt0 y coordinate
            
        #     self.slice_coord[i][1][0] = self.frame_width -1    # pt1 x coordinate
        #     self.slice_coord[i][1][1] = 0 +  i * slice_h    # pt1 y coordinate
            
        #     self.slice_coord[i][2][0] = self.frame_width -1   # pt2 x coordinate
        #     self.slice_coord[i][2][1] = (i+1)*slice_h - 1        # pt2 y coordinate
            
        #     self.slice_coord[i][3][0] = 0                     # pt3 x coordinate
        #     self.slice_coord[i][3][1] = (i+1)*slice_h -1         # pt3 y coordinate
def is_out_crop_region_old(self,vcam_crop_polygon, warp_polygon):

    vcam_p1_x = vcam_crop_polygon[0, 0]
    vcam_p1_y = vcam_crop_polygon[0, 1]
    vcam_p2_x = vcam_crop_polygon[1, 0]
    vcam_p2_y = vcam_crop_polygon[1, 1]
    vcam_p3_x = vcam_crop_polygon[2, 0]
    vcam_p3_y = vcam_crop_polygon[2, 1]
    vcam_p4_x = vcam_crop_polygon[3, 0]
    vcam_p4_y = vcam_crop_polygon[3, 1]

    is_p1_in_crop_rect = self.isPointinRect(vcam_p1_x, vcam_p1_y, warp_polygon)
    is_p2_in_crop_rect = self.isPointinRect(vcam_p2_x, vcam_p2_y, warp_polygon)
    is_p3_in_crop_rect = self.isPointinRect(vcam_p3_x, vcam_p3_y, warp_polygon)
    is_p4_in_crop_rect = self.isPointinRect(vcam_p4_x, vcam_p4_y, warp_polygon)

    if is_p1_in_crop_rect and is_p2_in_crop_rect and is_p3_in_crop_rect and is_p4_in_crop_rect:

        return False
    else:

        return True

def is_inner_region_old(self, crop_polygon):

        crop_polygon_p1_x = crop_polygon[0, 0]
        crop_polygon_p1_y = crop_polygon[0, 1]
        crop_polygon_p2_x = crop_polygon[1, 0]
        crop_polygon_p2_y = crop_polygon[1, 1]
        crop_polygon_p3_x = crop_polygon[2, 0]
        crop_polygon_p3_y = crop_polygon[2, 1]
        crop_polygon_p4_x = crop_polygon[3, 0]
        crop_polygon_p4_y = crop_polygon[3, 1]

        inner_roi_p1_x = self.inner_roi[0, 0]
        inner_roi_p1_y = self.inner_roi[0, 1]
        inner_roi_p2_x = self.inner_roi[1, 0]
        inner_roi_p2_y = self.inner_roi[1, 1]
        inner_roi_p3_x = self.inner_roi[2, 0]
        inner_roi_p3_y = self.inner_roi[2, 1]
        inner_roi_p4_x = self.inner_roi[3, 0]
        inner_roi_p4_y = self.inner_roi[3, 1]
        
        is_p1_in_inner_roi = self.isPointinRect(crop_polygon_p1_x, crop_polygon_p1_y, self.inner_roi)
        is_p2_in_inner_roi = self.isPointinRect(crop_polygon_p2_x, crop_polygon_p2_y, self.inner_roi)
        is_p3_in_inner_roi = self.isPointinRect(crop_polygon_p3_x, crop_polygon_p3_y, self.inner_roi)
        is_p4_in_inner_roi = self.isPointinRect(crop_polygon_p4_x, crop_polygon_p4_y, self.inner_roi)
        
        p1_dist = distance.euclidean((inner_roi_p1_x, inner_roi_p1_y), (crop_polygon_p1_x, crop_polygon_p1_y))
        p2_dist = distance.euclidean((inner_roi_p2_x, inner_roi_p2_y), (crop_polygon_p2_x, crop_polygon_p2_y))
        p3_dist = distance.euclidean((inner_roi_p3_x, inner_roi_p3_y), (crop_polygon_p3_x, crop_polygon_p3_y))
        p4_dist = distance.euclidean((inner_roi_p4_x, inner_roi_p4_y), (crop_polygon_p4_x, crop_polygon_p4_y))

        over_protrusion = max([p1_dist, p2_dist, p3_dist, p4_dist])

        if is_p1_in_inner_roi and is_p2_in_inner_roi and is_p3_in_inner_roi and is_p4_in_inner_roi:

            return True, over_protrusion

        else:

            return False, over_protrusion

   # Calculates Rotation Matrix given euler angles.
    def eulerAnglesToRotationMatrix(self,theta) :
        
        R_x = np.array([[1,         0,                  0                   ],
                        [0,         math.cos(theta[0]), -math.sin(theta[0]) ],
                        [0,         math.sin(theta[0]), math.cos(theta[0])  ]
                        ])
            
            
                        
        R_y = np.array([[math.cos(theta[1]),    0,      math.sin(theta[1])  ],
                        [0,                     1,      0                   ],
                        [-math.sin(theta[1]),   0,      math.cos(theta[1])  ]
                        ])
                    
        R_z = np.array([[math.cos(theta[2]),    -math.sin(theta[2]),    0],
                        [math.sin(theta[2]),    math.cos(theta[2]),     0],
                        [0,                     0,                      1]
                        ])
                        
                        
        R = np.dot(R_z, np.dot( R_y, R_x ))

        return R

    def cal_trans_matrix_in_euler(self, euler_p, eular_v):
        
        w = self.frame_width
        h = self.frame_height
        f = self.focal_in_pixel
        fx = self.fx
        fy = self.fy
        # Projection 2D -> 3D matrix
        invK = np.array([[1, 0, -w / 2], [0, 1, -h / 2], [0, 0, f]]).astype(float)

        K = np.linalg.inv(invK)

        # Composed rotation matrix with quaternion
        physical_R = self.eulerAnglesToRotationMatrix(euler_p)
        virtual_R = self.eulerAnglesToRotationMatrix(eular_v)


        S = np.array([[1.0 / fx, 0, 0], [0, 1.0 / fy, 0], [0, 0, 1]]).astype(float)

        R = np.dot(virtual_R, np.linalg.inv(physical_R))

        # Final transformation matrix

        return np.dot(np.dot(K, np.dot(R, invK)), S)
    
    def cal_slice_trans_matrix_proj(self,knee_pts_quat_p, quat_v):

        # the 4 points in the slice rectengle
        #  p0----------------p1
        #   |                 |    
        #  p3----------------p2

        slice_trans_matrices = []
        pb = np.zeros((4,2),dtype= "float32")

        # calculte first transform matrix of pt0 and pt1 
        quat_p = Quaternion(knee_pts_quat_p[0])
        pa = self.slice_coord[0]
        trans_matrix = self.cal_trans_matrix(quat_p,quat_v,1.0,1.0)
        pa0 = np.array([pa[0][0],pa[0][1],1])
        pa1 = np.array([pa[1][0],pa[1][1],1])
        pb0 = trans_matrix.dot(pa0)
        pb1 = trans_matrix.dot(pa1)
        pb[0][0] = pb0[0]/pb0[2]
        pb[0][1] = pb0[1]/pb0[2]
        pb[1][0] = pb1[0]/pb1[2]
        pb[1][1] = pb1[1]/pb1[2]
        
        for i in range(self.num_of_slice):
            
            # calculte transform matrix of pt2 and pt3
            quat_p = Quaternion(knee_pts_quat_p[i+1])
            trans_matrix = self.cal_trans_matrix(quat_p,quat_v,1.0,1.0)
            pa = self.slice_coord[i]
            pa2 = np.array([pa[2][0],pa[2][1],1])
            pa3 = np.array([pa[3][0],pa[3][1],1])
            pb2 = trans_matrix.dot(pa2)
            pb3 = trans_matrix.dot(pa3)
            
            # store tranformed points
            pb[2][0] = pb2[0]/pb2[2]
            pb[2][1] = pb2[1]/pb2[2]
            pb[3][0] = pb3[0]/pb3[2]
            pb[3][1] = pb3[1]/pb3[2]

            print('----------------------------')
            print('slice %d:'%i)
            print('pa[0] = [%.4f, %.4f], pb[0] = [%.4f, %.4f]'%(pa[0][0],pa[0][1],pb[0][0],pb[0][1]))
            print('pa[1] = [%.4f, %.4f], pb[1] = [%.4f, %.4f]'%(pa[1][0],pa[1][1],pb[1][0],pb[1][1]))
            print('pa[2] = [%.4f, %.4f], pb[2] = [%.4f, %.4f]'%(pa[2][0],pa[2][1],pb[2][0],pb[2][1]))
            print('pa[3] = [%.4f, %.4f], pb[3] = [%.4f, %.4f]'%(pa[3][0],pa[3][1],pb[3][0],pb[3][1]))
            this_slice_trans_matrix = cv2.getPerspectiveTransform(self.order_points(pa), self.order_points(pb))
            #this_slice_trans_matrix = self.getPerspectiveTransformMatrix(self.order_points(pa), self.order_points(pb))
            this_slice_trans_matrix = np.dot(this_slice_trans_matrix,self.scale_matrix)
            slice_trans_matrices.append(this_slice_trans_matrix)
            pb[0][0] = pb[3][0]
            pb[0][1] = pb[3][1]
            pb[1][0] = pb[2][0]
            pb[1][1] = pb[2][1]

        return slice_trans_matrices
    
    def order_points(self,pts):

        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype = "float32")
        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        # return the ordered coordinates
        return rect

    def getPerspectiveTransformMatrix(self,p1, p2):
        
        A = []
        for i in range(0, len(p1)):
            x, y = p1[i][0], p1[i][1]
            u, v = p2[i][0], p2[i][1]
            A.append([x, y, 1, 0, 0, 0, -u*x, -u*y, -u])
            A.append([0, 0, 0, x, y, 1, -v*x, -v*y, -v])
        A = np.asarray(A)
        U, S, Vh = np.linalg.svd(A)
        L = Vh[-1,:] / Vh[-1,-1]
        H = L.reshape(3, 3)


        return H

    def integrate_intra_frame_orein_in_lines(self, gyro_samples,cam_orien):   
        
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

        #interpolate camera orientaion in each line of a frame
        frame_cam_orein_in_lines = []
        t_start = gyro_samples[-1][0]
        t_end = gyro_samples[0][0]

        dt = (t_end - t_start)/(self.frame_height-1)

        for i in range(self.frame_height):
            t = t_start + i*dt
            for i in range(len(frame_cam_orien_in_samples)-1):
                t0, q0 = frame_cam_orien_in_samples[i]
                t1, q1 = frame_cam_orien_in_samples[i+1]
                if t >= t0 and t <= t1:
                    s_r = (t-t0) /(t1-t0)
                    q_interp = Quaternion.slerp(q0,q1,s_r)
                    
                    frame_cam_orein_in_lines.append(Quaternion(q_interp))
                    break
        
        return frame_cam_orein_in_lines
    def cal_inter_frame_motion_vector(self, vsync_timestamp, exptime, gyro_buffer):
        
        inter_frame_anlgle_x = 0
        inter_frame_anlgle_y = 0  
        inter_frame_anlgle_z = 0

        prev_frame_ts, current_frame_ts = self.cal_inter_frame_duration(vsync_timestamp, exptime)

        print('prev_frame_ts = %f, current_frame_ts = %f'%(prev_frame_ts, current_frame_ts))

        inter_frame_gyro_samples = self.extract_gyro_samples_from_buffer(gyro_buffer, prev_frame_ts, current_frame_ts)

        
        #check the inter-frame gyro data
        # print("\nframe samples:")
        # for i in range(len(inter_frame_gyro_samples)):
        #     print("ts = %f, gx = %f, gy = %f, gz = %f"
        #     %(inter_frame_gyro_samples[i][0],inter_frame_gyro_samples[i][1],inter_frame_gyro_samples[i][2],inter_frame_gyro_samples[i][3]))
        
        inter_frame_anlgle_x, inter_frame_anlgle_y, inter_frame_anlgle_z = self.cal_angular_from_angular_velocity(inter_frame_gyro_samples)
        
        
        return inter_frame_anlgle_x, inter_frame_anlgle_y, inter_frame_anlgle_z


    def cal_intra_frame_motion_vector(self, vsync_timestamp, exptime, gyro_buffer):
        

        first_line_ts, last_line_ts = self.cal_intra_frame_duration(vsync_timestamp, exptime)
        
        #print('first_line_ts = %f, last_line_ts = %f'%(first_line_ts, last_line_ts))
        
        expand_time = self.frame_duration / self.num_of_slice
        start_ts = first_line_ts - expand_time
        end_ts = last_line_ts + expand_time
        gyro_samples = self.extract_gyro_samples_from_buffer(gyro_buffer, start_ts, end_ts)

        num_of_gyro_samples = len(gyro_samples)

        frame_orien = []

        orien_x = 0
        orien_y = 0
        orien_z = 0


        for i in range(num_of_gyro_samples-1):

            t0, gx0, gy0, gz0 = gyro_samples[num_of_gyro_samples-i-1]
            t1, gx1, gy1, gz1 = gyro_samples[num_of_gyro_samples-i-2]

            dt = t1 -t0

            gx = (gx0 + gx1)*0.5
            gy = (gy0 + gy1)*0.5
            gz = (gz0 + gz1)*0.5

            orien_x += gx * dt
            orien_y += gy * dt
            orien_z += gz * dt

            frame_orien.append([t1, orien_x, orien_y, orien_z])


        # print("frame_orein:")
        # for i in range(len(frame_orien)):
        #     print('%f, %f, %f, %f'%(frame_orien[i][0],frame_orien[i][1],frame_orien[i][2],frame_orien[i][3]))

        slice_orien = []

        slice_duration = (last_line_ts - first_line_ts)/self.num_of_slice
        
        ts = first_line_ts + slice_duration
        
        for i  in range(self.num_of_slice):
            
            ts = min(ts, last_line_ts)

            #print('idx i = %d, ts = %f'%(i,ts))

            for j in range(len(frame_orien)-1):

                t0, orien_x0, orien_y0, orien_z0 = frame_orien[j]
                t1, orien_x1, orien_y1, orien_z1 = frame_orien[j+1]

                #print('t0 = %f, t1 = %f'%(t0,t1))

                if t0 <= ts and t1 >= ts:

                    orien_x = np.interp(ts, [t0, t1], [orien_x0, orien_x1])
                    orien_y = np.interp(ts, [t0, t1], [orien_y0, orien_y1])
                    orein_z = np.interp(ts, [t0, t1], [orien_z0, orien_z1])
                    
                    slice_orien.append([orien_x, orien_y,orein_z])
                    #print('ts = %f, orein_x, =%f, orein_y = %f, orein_z = %f'%(ts,orien_x, orien_y, orein_z))

                    break

            ts = slice_duration + ts


        return slice_orien

    