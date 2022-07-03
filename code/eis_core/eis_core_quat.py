import numpy as np
from pyquaternion import Quaternion
import ipdb

def quaternion_to_euler_angle(quat):
    w = quat[0]
    x = quat[1]
    y = quat[2]
    z = quat[3]
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = np.arctan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = np.where(t2>+1.0,+1.0,t2)
    #t2 = +1.0 if t2 > +1.0 else t2

    t2 = np.where(t2<-1.0, -1.0, t2)
    #t2 = -1.0 if t2 < -1.0 else t2
    Y = np.arcsin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = np.arctan2(t3, t4)

    return X, Y, Z 


def from_euler_angles(alpha, beta, gamma):
    
    # Set up the output array
    R = np.array([0,0,0,0],dtype=np.float)

    # Compute the actual values of the quaternion components
    R[0] =  np.cos(beta/2)*np.cos((alpha+gamma)/2)  # scalar quaternion components
    R[1] = -np.sin(beta/2)*np.sin((alpha-gamma)/2)  # x quaternion components
    R[2] =  np.sin(beta/2)*np.cos((alpha-gamma)/2)  # y quaternion components
    R[3] =  np.cos(beta/2)*np.sin((alpha+gamma)/2)  # z quaternion components


    return quaternion.quaternion(R[0],R[1],R[2],R[3])


def as_rotation_matrix(q):

    
    _eps = 1e-14 
    n = q.norm() # square sum of quaternion

    if n == 0.0:
        raise ZeroDivisionError("Input to `as_rotation_matrix({0})` has zero norm".format(q))
    elif abs(n-1.0) < _eps:  # Input q is basically normalized
        return np.array([
            [1 - 2*(q.y**2 + q.z**2),   2*(q.x*q.y - q.z*q.w),      2*(q.x*q.z + q.y*q.w)],
            [2*(q.x*q.y + q.z*q.w),     1 - 2*(q.x**2 + q.z**2),    2*(q.y*q.z - q.x*q.w)],
            [2*(q.x*q.z - q.y*q.w),     2*(q.y*q.z + q.x*q.w),      1 - 2*(q.x**2 + q.y**2)]
        ])
    else:  # Input q is not normalized
        return np.array([
            [1 - 2*(q.y**2 + q.z**2)/n,   2*(q.x*q.y - q.z*q.w)/n,      2*(q.x*q.z + q.y*q.w)/n],
            [2*(q.x*q.y + q.z*q.w)/n,     1 - 2*(q.x**2 + q.z**2)/n,    2*(q.y*q.z - q.x*q.w)/n],
            [2*(q.x*q.z - q.y*q.w)/n,     2*(q.y*q.z + q.x*q.w)/n,      1 - 2*(q.x**2 + q.y**2)/n]
        ])


# def quaternion_multiply(quaternion1, quaternion0):
    
#     w0, x0, y0, z0 = quaternion0
#     w1, x1, y1, z1 = quaternion1
#     R[0] = -x1*x0 - y1*y0 - z1*z0 + w1*w0
#     R[1] = x1*w0 + y1*z0 - z1*y0 + w1*x0
#     R[2] = -x1*z0 + y1*w0 + z1*x0 + w1*y0
#     R[3] = x1*y0 - y1*x0 + z1*w0 + w1*z0
    
#     return  quaternion.quaternion(R[0],R[1],R[2],R[3])