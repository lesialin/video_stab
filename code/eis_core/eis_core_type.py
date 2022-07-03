

class CMOSDATA:

    def __init__(self, vsync_ts = 0.0, exptime = 0.0):

        self.vsync_ts = vsync_ts  # in sec 
        self.exptime = exptime   # in sec

class GYRODATA:

    def __init__(self, ts = 0.0,gx = 0.0,gy = 0.0, gz = 0.0):

        self.ts = ts  # timestamp in sec 
        self.gx = gx  # in rad/sec
        self.gy = gy  # in rad/se
        self.gz = gz  # in rad/se


class EISParam:
    
    def __init__(self):

        self.crop_ratio = 0.1
        self.alpha = 0.95
        self.alpha_min = 1.0
        self.alpha_max = 0
        self.beta = 2.6
        self.gamma = 0.95
        self.damping = 0.95
        self.inner_padding_ratio = 0.0
        self.lookahead_no = 0
        self.knee_point = 10
        self.use_nonlinear_filter = True
        
        

class CMOSParam:

    def __init__(self):
        self.blanking = 99 #TODO: replace to rolling shutter time
        self.cmos_frame_height = 3564
        self.cmos_frame_width = 4056
        self.effective_height = 2160
        self.effective_width = 3480
        self.focal_in_mm = 4.73
        self.sensor_width_in_mm = 7.564


class GyroParam:

    def __init__(self):

        self.gyro_bias = [0.0,0.0,0.0]
        self.sample_rate = 500
    

class DebugParam:

    def __init__(self):

        self.eis_pass1 = True
        self.eis_pass2 = True
        self.rs_correct_off = True
        self.test_mode = True
        self.preserve_margin = True
        self.test_frame_no = 0
        self.start_frame_no = 0
        self.log_image = True
        self.use_opengl = True
        self.warp_with_resize = True
        self.show_plot = False
        

class VideoParam:

    def __init__(self):

        self.frame_height = 1080
        self.frame_width = 1920
        self.frame_rate = 30
        self.preview_height = 720
        self.preview_width = 1280


class SiggenParam:

    def __init__(self):
        self.gyro_log_idx = [0,1,2,3]
        self.gyro_time_scale_exp = 6
        self.cmos_time_scale_exp = 6
        self.gyro_time_scale = 1
        self.cmos_time_scale = 1

