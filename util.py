import math
def toHexCmd(cmd):
    #convert -1 to 1 to 0 to 32768
    cmd = math.floor(32768 * (cmd +1) /2)
    if cmd < 0:
        return 0
    if cmd > 32768:
        return 32768
    return cmd