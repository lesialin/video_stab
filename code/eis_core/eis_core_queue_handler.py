import numpy as np
import math
import config_path
from eis_core import eis_core_type
from eis_core import eis_core_config_loader
import ipdb

class RingBuffer:

    # class that implements a not-yet-full buffer
    def __init__(self,size_max):

        self.max = size_max
        self.data = []

    class __Full:

        # class that implements a full buffer
        def append(self, x):
            # Append an element overwriting the oldest one.
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.max
        
        def get(self):
            # return list of elements in correct order
            return self.data[self.cur:]+self.data[:self.cur]

    def append(self,x):
        # append an element at the end of the buffer
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = self.__Full

    def get(self):
        # Return a list of elements from the oldest to the newest. 
        return self.data



class EISGyroQueue(object):

    def __init__(self,video_frame_rate):

        scale = 2 # scale buffer size for safety

        self.gyro_param = eis_core_config_loader.load_gyro_config(config_path.gyro_config_path)
        coord_trans_matrix = eis_core_config_loader.load_coord_trans_matrix_config(config_path.coord_trans_matrix_config_path)    
        self.max_gyro_in_frame_no = int(self.gyro_param.sample_rate / video_frame_rate + 0.5) +1
        buffer_size = int(self.gyro_param.sample_rate / video_frame_rate *scale)
        
        self.coord_trans_matrix = coord_trans_matrix
        
        #gyro queue
        self.gyro_queue = RingBuffer(buffer_size)

    def __getitem__(self,key):
        
        gyro_data = self.gyro_queue.get()[key]
        
        return gyro_data.ts, gyro_data.gx, gyro_data.gy, gyro_data.gz
    
    def append(self,timestamp, gx, gy, gz):

        # coordinate system  from gyro x/y/z to camera x/y/z
        angular_velocity = np.dot(np.array([gx,gy,gz]),np.array(self.coord_trans_matrix)) 
        #gyro_data = eis_core_type.GYRODATA(timestamp,angular_velocity[0] / 180 * math.pi, angular_velocity[1] / 180 * math.pi, angular_velocity[2] / 180 * math.pi)
        gyro_data = eis_core_type.GYRODATA(timestamp,angular_velocity[0]-self.gyro_param.gyro_bias[0], angular_velocity[1]-self.gyro_param.gyro_bias[1], angular_velocity[2]-self.gyro_param.gyro_bias[2])
        self.gyro_queue.append(gyro_data)

    def size(self):

        return len(self.gyro_queue.get())

    def copy(self):

        return self.gyro_queue.get()





   