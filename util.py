import math
from  math import acos,sqrt
import numpy as np
def toHexCmd(cmd):
    #convert -1 to 1 to 0 to 32768
    cmd = math.floor(32768 * (cmd +1) /2)
    if cmd < 0:
        return 0
    if cmd > 32768:
        return 32768
    return cmd

def toAxisAngle(quat):
    qw = quat[0]
    qx = quat[1]
    qy = quat[2]
    qz = quat[3]
    s = sqrt(1-qw*qw)
    angle = 2 * acos(qw)
    if s < 0.001:
        x = qx
        y = qy
        z = qz
        return np.array([angle * x, angle * y, angle * z])
    else:
        x = qx / sqrt(1 - qw * qw)
        y = qy / sqrt(1 - qw * qw)
        z = qz / sqrt(1 - qw * qw)
        return np.array([angle*x,angle*y,angle*z])

def JoyEXP(v,exp):
    if math.fabs(v) < 0.001:
        return 0
    return math.pow(math.fabs(v),exp)* v / math.fabs(v)