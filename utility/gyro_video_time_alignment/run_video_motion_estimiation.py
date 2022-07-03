import cv2
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import ipdb
import glob

if len(sys.argv)!=2:
    print("Please enter: run_motion_estimation.py log_dir")
    exit()
else:
    log_dir = sys.argv[1]

#result log path
result_dir = log_dir + '/motion_vector'

if not os.path.exists(result_dir):
    os.makedirs(result_dir)

motion_vector_path = result_dir + '/motion_vector.log'

# load video
video_ext_path = log_dir + '/*.mp4'
video_filename = glob.glob(video_ext_path)[0].split('/')[-1]
video_path = log_dir + '/' + video_filename

video = cv2.VideoCapture(video_path)

#Get frame count
n_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

# Read first frame
_, prev = video.read()
 
# Convert frame to grayscale
prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
# Pre-define transformation-store array
transforms = np.zeros((n_frames-1, 3), np.float32) 

for i in range(n_frames-2):

    # Detect feature points in previous frame
    prev_pts = cv2.goodFeaturesToTrack(prev_gray,
                                        maxCorners=200,
                                        qualityLevel=0.01,
                                        minDistance=30,
                                        blockSize=3)

    # Read next frame
    success, curr = video.read() 
    if not success: 
        break 

    # Convert to grayscale
    curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY) 

    # Calculate optical flow (i.e. track feature points)
    curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None) 

    # Sanity check
    assert prev_pts.shape == curr_pts.shape 

    # Filter only valid points
    idx = np.where(status==1)[0]
    prev_pts = prev_pts[idx]
    curr_pts = curr_pts[idx]

    #Find transformation matrix
    #m = cv2.estimateRigidTransform(prev_pts, curr_pts, fullAffine=False) #will only work with OpenCV-3 or less
    m, _n =	cv2.estimateAffinePartial2D(prev_pts, curr_pts)

    # Extract traslation
    dx = m[0,2]
    dy = m[1,2]

    # Extract rotation angle
    da = np.arctan2(m[1,0], m[0,0])

    # Store transformation
    transforms[i] = [dx,dy,da]

    # Move to next frame
    prev_gray = curr_gray

    print("Frame: " + str(i) +  "/" + str(n_frames) + " -  Tracked points : " + str(len(prev_pts)))



# write motion vectors to log
f_mv = open(motion_vector_path, 'w')

for i in range(len(transforms)):

    f_mv.write('%.6f %.6f %.6f\n'%(transforms[i,0],transforms[i,1],transforms[i,2]))


f_mv.close()