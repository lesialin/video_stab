# Video Stabilization

This repo is to implementation video stabilization by gyroscope, which is based on paper [A Non-Linear Filter for Gyroscope-Based Video
Stabilization](https://research.nvidia.com/sites/default/files/pubs/2014-09_A-Non-Linear-Filter/bell_troccoli_pulli_eccv2014.pdf)


The simulation of vid_stab flow is as below, 

![](image/EIS_sys.png)


#### configuration

The configuration in config/ folder, include:

**debug_config.json**

- test_mode: in test_mode you can test log in _test_frame_no_ 
- start_frame_no: run the video start from _start_frame_no_
- preserve_margin: crop the outer margin or not
- log_image: log result comparison frame 
  
```
{
    "eis_pass1": true,
    "eis_pass2":false,
    "rs_correct_off": false,
    "test_mode":false,
    "test_frame_no": 100,
    "start_frame_no":0,
    "preserve_margin":false,
    "log_image":true   
    
  }

```

**eis_config.json**

- crop_ratio: crop ratio, ex 0.1 means crop 10% height/width each side
- alpha: low-pass filter coefficient, if use constant filter
- alpha_min: the minimum low-pass filter coefficient, if use non-linear filter
- alpha_max: the maximum low-pass filter coefficient, if use non-linear filter
- beta: the low-pass filter response coefficient
- gamma: the low-pass filter coefficient for the lookahead frame motion
- inner_padding_ratio: the inner padding ratio of crop region
- lookhead_no: the lookahead frame number 
- knee_point: knee point number for image warp
- use_nonlinear_filter:use non-linear filter or not

```
{
    "crop_ratio": 0.1,
    "alpha": 0.9,
    "alpha_min": 0.75,
    "alpha_max": 0.95,
    "beta": 1.0,
    "gamma": 0.9,
    "damping": 0.95,
    "inner_padding_ratio": 0.0,
    "lookahead_no": 10,
    "knee_point": 39,
    "use_nonlinear_filter": true
  }
```

**gyro_sensor_config.json**

```
{
    "gyro_bias": [
        2.68081035e-04,
        -5.34824714e-04,
        -9.35238864e-05
    ],
    "sample_rate": 460
}
```

**coord_trans_matrix.json**

```
{
    "coordinate_trans_matrix":[
        [1,0,0],
        [0,1,0],
        [0,0,1]
    ]
}
```

**video_config.json**

```
{
    "preview_height": 720,
    "preview_width": 1280
}
```

**cmos_sensor_config.json**

- blanking: the blanking number of the cmos frame
  
- 
```
{
    "blanking": 68,
    "cmos_frame_height": 3000,
    "cmos_frame_width": 4000,
    "effective_height": 2256,
    "effective_width": 4000,
    "focal_in_mm": 4.74,
    "sensor_width_in_mm": 6.4
}
```

**siggen_config.json**

- gyro_log_idx: the order in gyro log 
- gyro_time_scale_exp: the timestamp scale in exp
- cmos_time_scale_exp: the timestamp scale in exp
  
```
{
    "gyro_log_idx": [0,1,2,3],
    "gyro_time_scale_exp": 7,
    "cmos_time_scale_exp": 7
    
}

```

