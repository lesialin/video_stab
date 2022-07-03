from collections import deque
import numpy as np
import time
import config_path
from eis_core import eis_core_type
from eis_core import eis_core_config_loader
from threading import Thread
import ipdb

class EIS_SIGNAL(Thread):

    def __init__(self,cmos_log_path, gyro_log_path,gyro_buffer,time_delay,condition):
        
        

        Thread.__init__(self)

        siggen_param = eis_core_config_loader.load_siggen_config(config_path.siggen_config_path)
        
        self.cmos_exp = siggen_param.cmos_time_scale_exp
        self.gyro_exp = siggen_param.gyro_time_scale_exp
        self.cmos_scale = siggen_param.cmos_time_scale
        self.gyro_scale = siggen_param.gyro_time_scale
        gyro_idx = siggen_param.gyro_log_idx

        self.condition = condition

        self.gyro_buffer = gyro_buffer

        print("load cmos log....")
        # read cmos sensor log
        self.cmos_sensor_log = np.loadtxt(cmos_log_path)
        # cmos sensor initialize
        self.cmos_sensor = CMOS_SENSOR(deque(self.cmos_sensor_log))
        
        print("load gyro log....")
        # read gyro log
        self.gyro_sensor_log = np.loadtxt(gyro_log_path)
        # gyro sensor initialize
        self.gyro_sensor = GYRO_SENSOR(deque(self.gyro_sensor_log[:,gyro_idx]))# TODO: orginize in unifteformat 
        
        # cmos time clock
        self.cmos_timer = deque(self.cmos_scale*self.cmos_sensor_log[:,0]/10**self.cmos_exp)
        # gyro time clock
        self.gyro_timer = deque(self.gyro_scale*self.gyro_sensor_log[:,0]/10**self.gyro_exp + time_delay)
        
        self.activate = True
        
        self.run_signal_type = None

        self.current_gyro_ts = self.gyro_timer.popleft()

        self.current_cmos_ts = self.cmos_timer.popleft()

        self.current_ts = 0.0

        self.prev_ts = 0.0

        self.gyro_in_frame_count = 0

        self.max_gyro_in_frame_no = gyro_buffer.max_gyro_in_frame_no
        
        self.cmos_sig = []

        self.gyro_sig = []

        if self.current_cmos_ts < self.current_gyro_ts:

            self.run_signal_type = 'cmos'
            self.current_ts = self.current_cmos_ts
        
        else:
            self.run_signal_type = 'gyro'
            self.current_ts = self.current_gyro_ts

        self.prev_ts = self.current_ts


    def run(self):
        

        while self.activate:
            
            
            if self.run_signal_type =='cmos':
                
                #set gyro count as vsync coming
                self.gyro_in_frame_count = 0                
                
                cmos_sig = self.cmos_sensor.run()

                self.condition.acquire()	#获取条件锁
                
                self.cmos_sig = cmos_sig
                
                self.condition.notify()	   # 唤醒消费者线程
                self.condition.release()	#释放条件锁
                
                self.current_cmos_ts = self.cmos_timer.popleft()

                if len(self.cmos_timer) == 0:

                    print("cmos_sensor not activate!")
                    self.cmos_sensor.activate = False

            else:

                if self.gyro_in_frame_count > self.max_gyro_in_frame_no:
                    
                    self.condition.acquire()	#获取条件锁
                    self.condition.notify()	   # 唤醒消费者线程
                    self.condition.release()	#释放条件锁
                    #set gyro count as vsync coming
                    self.gyro_in_frame_count = 0                


                self.gyro_in_frame_count+= 1

                #print('gyro_count = %d'%self.gyro_in_frame_count)
                
                # run gyro sensor
                gyro_sig = self.gyro_sensor.run()

                # push to gyro_buffer
                self.gyro_buffer.append(self.gyro_scale*gyro_sig[0]/10**self.gyro_exp,gyro_sig[1],gyro_sig[2],gyro_sig[3])

                # get current gyro timestamp                
                self.current_gyro_ts = self.gyro_timer.popleft()

                if  len(self.gyro_timer) == 0:

                    print("gyro_sensor not activate!")
                    self.gyro_sensor.activate = False
            
            
            if (not self.gyro_sensor.activate) or (not self.cmos_sensor.activate):
                print('singal activate set to false and break')    
                self.activate = False
                
                break
                
            

            #store current timestamp
            self.prev_ts = self.current_ts

            if self.current_cmos_ts < self.current_gyro_ts:

                self.run_signal_type = 'cmos'
                self.current_ts = self.current_cmos_ts
            else:
                self.run_signal_type = 'gyro'
                self.current_ts = self.current_gyro_ts

            #print("current ts = %f, prev_ts = %f, wait for %f"%(self.current_ts,self.prev_ts, self.current_ts -self.prev_ts))

            time.sleep(self.current_ts - self.prev_ts)   
            


class CMOS_SENSOR:

    def __init__(self, log_buffer):
        
        self.sensor_log_buffer = log_buffer    
        self.activate = True
        self.frame_count = 0
        self.debug_param = eis_core_config_loader.load_debug_config(config_path.debug_config_path)

    def run(self):
        
        cmos_sig = []

        if len(self.sensor_log_buffer)> 0:
            
            cmos_sig = self.sensor_log_buffer.popleft()
            self.frame_count+=1
            
            if len(self.sensor_log_buffer) ==0:
                
                self.activate = False
            
            print('cmos signal frame_count = %d'%self.frame_count)
            
            if self.debug_param.test_mode:
                
                if self.frame_count > self.debug_param.test_frame_no:

                    self.activate = False
                

        return cmos_sig




class GYRO_SENSOR:

    def __init__(self, log_buffer):
        
        self.sensor_log_buffer = log_buffer    
        self.activate = True


    def run(self):
        
        gyro_sig = []

        if len(self.sensor_log_buffer)> 0:
            
            gyro_sig = self.sensor_log_buffer.popleft()
            
            if len(self.sensor_log_buffer) ==0:
                self.activate = False

        return gyro_sig
