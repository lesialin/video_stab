import sys
import os
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv)!=2:
    print('please enter: run_gyro_bias_calculation.py log_dir/')
    exit()
else:
    log_dir = sys.argv[1]

result_dir = log_dir + '/result'

if not os.path.exists(result_dir):
    os.makedirs(result_dir)

imu_log_path = log_dir + '/imu.log'
imu_data = np.loadtxt(imu_log_path)

gyro_data = imu_data[:,1:]

num_of_gyro = len(gyro_data)

start_idx  = int(0.25*num_of_gyro)
end_idx = num_of_gyro- start_idx
gyro_data = gyro_data[start_idx:end_idx,:]

bias = np.mean(gyro_data,0)
print('gyro bias:')
print(bias)

gyro_filepath = result_dir + '/gyro_bias.json'
f = open(gyro_filepath,'w+')
f.write("{\n")
f.write('\t\"gyro_bias\": [\n\t\t%e,\n\t\t%e,\n\t\t%e\n\t\t]\n}\n'%(bias[0],bias[1],bias[2]))
f.close()

fig = plt.figure(figsize=(20,10))
plt.plot(gyro_data[:,0],label='axis0')
plt.plot(gyro_data[:,1],label='axis1')
plt.plot(gyro_data[:,2],label='axis2')
plt.xlabel("gyro_sample")
plt.ylabel("angular velocity")
plt.title("origin gyro data")
plt.legend()
plt.savefig("%s/origin_gyro.png"%result_dir)
plt.show(block=False)
plt.pause(1)
plt.close(fig)


fig = plt.figure(figsize=(20,10))
plt.plot(gyro_data[:,0]-bias[0],label='axis0')
plt.plot(gyro_data[:,1]-bias[1],label='axis1')
plt.plot(gyro_data[:,2]-bias[2],label='axis2')
plt.xlabel("gyro_sample")
plt.ylabel("angular velocity")
plt.title("calibrated gyro data")
plt.legend()
plt.savefig("%s/calibrated_gyro.png"%result_dir)
plt.show(block=False)
plt.pause(1)
plt.close(fig)


