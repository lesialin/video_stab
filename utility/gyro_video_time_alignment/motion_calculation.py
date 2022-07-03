import numpy as np

def extract_gyro_samples_from_buffer(gyro_buffer, start_timestamp, end_timestamp):
        
        gyro_samples = []
        buffer_size = len(gyro_buffer)
        idx = buffer_size

        # interpolate last gyro sample
        for i in reversed(range(buffer_size)):

            t1 =  gyro_buffer[i,0]
            gx1 = gyro_buffer[i,1]
            gy1 = gyro_buffer[i,2]
            gz1 = gyro_buffer[i,3]

            t0 =  gyro_buffer[i-1,0]
            gx0 = gyro_buffer[i-1,1]
            gy0 = gyro_buffer[i-1,2]
            gz0 = gyro_buffer[i-1,3]


            if t1 >= end_timestamp and end_timestamp >= t0:

                gx = np.interp(end_timestamp, [t0, t1], [gx0, gx1])
                gy = np.interp(end_timestamp, [t0, t1], [gy0, gy1])
                gz = np.interp(end_timestamp, [t0, t1], [gz0, gz1])
                
                # check the interpolation result
                #print("t0 =     %f, gx0 = %f, gy0 = %f, gz0 = %f"%(t0, gx0, gy0, gz0))
                #print("cur_ts = %f, gx  = %f, gy  = %f, gz  = %f"%(end_timestamp,gx, gy,gz))
                #print("t1 =     %f, gx1 = %f, gy1 = %f, gz1 = %f"%(t1, gx1, gy1, gz1))
                
                gyro_samples.append([end_timestamp, gx, gy, gz])
                
                # record the index 
                idx = i-1
                #print("stop to idx = %d"%idx)

                break
        
        for i in reversed(range(idx+1)):

            t =  gyro_buffer[i,0]
            gx = gyro_buffer[i,1]
            gy = gyro_buffer[i,2]
            gz = gyro_buffer[i,3]
            
            if t > start_timestamp:
                gyro_samples.append([t, gx, gy, gz])
            else: 
                idx = i
                #print("stop to idx = %d"%idx)
                break

        t1 =  gyro_buffer[i+1,0]
        gx1 = gyro_buffer[i+1,1]
        gy1 = gyro_buffer[i+1,2]
        gz1 = gyro_buffer[i+1,3]

        t0 =  gyro_buffer[i,0]
        gx0 = gyro_buffer[i,1]
        gy0 = gyro_buffer[i,2]
        gz0 = gyro_buffer[i,3]

        gx = np.interp(start_timestamp, [t0, t1], [gx0, gx1])
        gy = np.interp(start_timestamp, [t0, t1], [gy0, gy1])
        gz = np.interp(start_timestamp, [t0, t1], [gz0, gz1])

        # check the interpolation result
        #print("t0 =     %f, gx0 = %f, gy0 = %f, gz0 = %f"%(t0, gx0, gy0, gz0))
        #print("prev_ts= %f, gx  = %f, gy  = %f, gz  = %f"%(prev_frame_ts,gx, gy,gz))
        #print("t1 =     %f, gx1 = %f, gy1 = %f, gz1 = %f"%(t1, gx1, gy1, gz1))

        gyro_samples.append([start_timestamp, gx, gy, gz])

        
        return gyro_samples

def cal_angular_from_angular_velocity(gyro_samples):

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
