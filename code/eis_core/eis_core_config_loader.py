import json
import cv2
from eis_core import eis_core_type

def load_eis_config(config_path):
    
    eis_param = eis_core_type.EISParam()
    
    with open(config_path , 'r') as reader:
        config_in_js = json.loads(reader.read())

    eis_param.crop_ratio  = config_in_js["crop_ratio"]
    eis_param.alpha = config_in_js["alpha"]
    eis_param.alpha_min = config_in_js["alpha_min"]
    eis_param.alpha_max = config_in_js["alpha_max"]
    eis_param.beta = config_in_js["beta"]
    eis_param.gamma = config_in_js["gamma"]
    eis_param.damping = config_in_js["damping"]
    eis_param.inner_padding_ratio = config_in_js["inner_padding_ratio"]
    eis_param.lookahead_no = config_in_js["lookahead_no"]
    eis_param.knee_point = config_in_js["knee_point"]
    eis_param.use_nonlinear_filter = config_in_js["use_nonlinear_filter"]
    

    return eis_param


def load_cmos_config(config_path):

    cmos_param = eis_core_type.CMOSParam
    
    with open(config_path , 'r') as reader:
        config_in_js = json.loads(reader.read())

    cmos_param.blanking = config_in_js["blanking"]
    cmos_param.cmos_frame_height = config_in_js["cmos_frame_height"]
    cmos_param.cmos_frame_width = config_in_js["cmos_frame_width"]
    cmos_param.effective_width = config_in_js["effective_width"]
    cmos_param.effective_height = config_in_js["effective_height"]
    cmos_param.focal_in_mm = config_in_js["focal_in_mm"]
    cmos_param.sensor_width_in_mm = config_in_js["sensor_width_in_mm"]

    return cmos_param


def load_gyro_config(config_path):

    gyro_param = eis_core_type.GyroParam
    with open(config_path , 'r') as reader:
        config_in_js = json.loads(reader.read())

    gyro_param.gyro_bias = config_in_js["gyro_bias"]
    gyro_param.sample_rate = config_in_js["sample_rate"]

    return gyro_param


def load_video_config(config_path, frame_width, frame_height, frame_rate):

    video_param = eis_core_type.VideoParam
    with open(config_path , 'r') as reader:
        config_in_js = json.loads(reader.read())

    video_param.frame_height = frame_height
    video_param.frame_width = frame_width
    video_param.frame_rate = frame_rate
    video_param.preview_height = config_in_js["preview_height"]
    video_param.preview_width = config_in_js["preview_width"]
    
    return video_param


def load_debug_config(config_path):
    
    debug_param = eis_core_type.DebugParam
    with open(config_path , 'r') as reader:
        config_in_js = json.loads(reader.read())

    debug_param.eis_pass1 = config_in_js["eis_pass1"]
    debug_param.eis_pass2 = config_in_js["eis_pass2"]
    debug_param.rs_correct_off = config_in_js["rs_correct_off"]
    debug_param.test_frame_no = config_in_js["test_frame_no"]
    debug_param.start_frame_no = config_in_js["start_frame_no"]
    debug_param.test_mode = config_in_js["test_mode"]
    debug_param.preserve_margin = config_in_js["preserve_margin"]
    debug_param.log_image = config_in_js["log_image"]
    debug_param.use_opengl = config_in_js["use_opengl"]
    debug_param.warp_with_resize = config_in_js["warp_with_resize"]
    debug_param.show_plot = config_in_js["show_plot"]
    
    return debug_param


def load_coord_trans_matrix_config(config_path):
    
    with open(config_path , 'r') as reader:
        config_in_js = json.loads(reader.read())

    coord_trans_matrix =  config_in_js["coordinate_trans_matrix"]

    return coord_trans_matrix


def load_siggen_config(config_path):
    
    siggen_param = eis_core_type.SiggenParam
    
    with open(config_path , 'r') as reader:
        config_in_js = json.loads(reader.read())

    siggen_param.gyro_log_idx = config_in_js["gyro_log_idx"]
    siggen_param.gyro_time_scale_exp = config_in_js["gyro_time_scale_exp"]
    siggen_param.cmos_time_scale_exp = config_in_js["cmos_time_scale_exp"]
    siggen_param.gyro_time_scale = config_in_js["gyro_time_scale"]
    siggen_param.cmos_time_scale = config_in_js["cmos_time_scale"]

    return siggen_param
    




