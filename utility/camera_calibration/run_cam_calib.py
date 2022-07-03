import sys
import cv2
import numpy as np
import os
import glob
import ipdb

if len(sys.argv)!=4:
    print('please enter: python run_cam_calib.py image_path chess_width_dim chess_height_dim')
    exit()
else:
    image_path = sys.argv[1]
    chess_width_dim = int(sys.argv[2])
    chess_height_dim = int(sys.argv[3])
    

square_size = 2.0


result_image_path = image_path + '/result/'
if not os.path.exists(result_image_path):
    os.makedirs(result_image_path)

# Defining the dimensions of checkerboard
CHECKERBOARD = (chess_height_dim,chess_width_dim)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Creating vector to store vectors of 3D points for each checkerboard image
objpoints = []
# Creating vector to store vectors of 2D points for each checkerboard image
imgpoints = [] 


# Defining the world coordinates for 3D points
objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= square_size

prev_img_shape = None


# Extracting path of individual image stored in a given directory
img_path_with_ext = image_path + '/*.jpg'
images = glob.glob(img_path_with_ext)
i = 0
j = 0
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    h,w = gray.shape
    ipdb.set_trace()
    # Find the chess board corners
    # If desired number of corners are found in the image then ret = true
    print("find chessboardcorner in %d image"%i)
    if h > 2000:
        small_gray = cv2.resize(gray,(w//2,h//2))
        ret, corners = cv2.findChessboardCorners(small_gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

        if ret==True:
            corners = 2*corners     
    else:
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    
    """
    If desired number of corner are detected,
    we refine the pixel coordinates and display 
    them on the images of checker board
    """
    if ret == True:
        print("image %d find corner!"%i)
        j = j+1
        objpoints.append(objp)
        # refining pixel coordinates for given 2d points.
        corners2 = cv2.cornerSubPix(gray, corners, (5,5),(-1,-1), criteria)
        
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
    
        img_filename  = result_image_path + '/chess_img_%02d_find.jpg'%i
    else:
        img_filename  = result_image_path + '/chess_img_%02d_not_find.jpg'%i

    i = i +1
    cv2.imwrite(img_filename,img)
    
find_ratio = j/i
print('the ratio of findcorner is %f'%(find_ratio))

"""
Performing camera calibration by 
passing the value of known 3D points (objpoints)
and corresponding pixel coordinates of the 
detected corners (imgpoints)
"""


ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

mean_error = 0

for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error


avg_error = mean_error/len(objpoints)

print("\nrms: %f, error: %f\n"%(ret,avg_error))
print("Camera matrix : \n")
print(mtx)
print("dist : \n")
print(dist)



fc = open('%s/calib.txt'%result_image_path,'w+')
fc.write('camera_intrinsc:\n')
fc.write('-------------------------------------------------------\n')
fc.write('rms: %f, error: %f\n\n'%(ret,avg_error))
fc.write('camera matrix:\n')
fc.write('[ %e, %e, %e]\n'%(mtx[0][0],mtx[0][1],mtx[0][2]))
fc.write('[ %e, %e, %e]\n'%(mtx[1][0],mtx[1][1],mtx[1][2]))
fc.write('[ %e, %e, %e]\n'%(mtx[2][0],mtx[2][1],mtx[2][2]))
fc.write('\ndistortion:\n[%e, %e, %e, %e, %e]\n'%(dist[0][0],dist[0][1],dist[0][2],dist[0][3],dist[0][4]))
fc.write('-------------------------------------------------------\n')
fc.write('\n %f %% image can find corner\n'%(find_ratio*100))
fc.close()





# #camera matrix with lens distortion
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,gray.shape[::-1],0,gray.shape[::-1])

i = 0
for fname in images:
    img = cv2.imread(fname)
    # undistort
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # crop the image
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]
    i=i+1
    
    undist_and_dist_img =cv2.vconcat([img,dst])
    img_filename  = result_image_path + '/undist_img_%02d.jpg'%i
    cv2.imwrite(img_filename, undist_and_dist_img)
    




