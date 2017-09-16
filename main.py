from pymavlink import mavutil
from pymavlink.quaternion import  *
import sys
import win32api,win32con
import math
import pyvjoy
import threading
from proxy_8111 import proxy_8111
from wt_server import *
from util import *
import pygame

class game_aircraft_control:
    def __init__(self):
        pygame.joystick.init()
        self.t16000m = None
        for k in range(pygame.joystick.get_count()):
            if pygame.joystick.Joystick(k).get_name() == "T.16000M":
                self.t16000m = pygame.joystick.Joystick(k)


master = mavutil.mavlink_connection("COM3", baud="230400")

global q_base
q_base = None

global joy
joy = pyvjoy.VJoyDevice(1)

from pynput.keyboard import Key, Listener

def on_press(key):
    if key == Key.f9:
        print("reset joystick pov")
        global q_base
        q_base = None

def on_release(key):
    pass


global cmdxyz
cmdxyz = None
def proccess_messages(m):
    '''show incoming mavlink messages'''
    print("Starting recieve data")
    while True:
        msg = m.recv_match(blocking=True)
        if not msg:
            continue
        if msg.get_type() == "BAD_DATA":
            if mavutil.all_printable(msg.data):
                #sys.stdout.write(msg.data)
                sys.stdout.flush()
        else:
            if msg._type == "ATTITUDE_QUATERNION":
                q_now = QuaternionBase(attitude=[msg.q1, msg.q2, msg.q3, msg.q4])
                global q_base
                if q_base is None:
                    q_base = q_now.inversed
                q_now = q_base.__mul__(q_now)
                eul = q_now.euler * 180 / 3.14
                global cmdxyz
                if cmdxyz is None:
                    cmdxyz = eul / 180
                else:
                    cmdxyz = eul / 180 * 0.3 + cmdxyz * 0.7
                #win32api.mouse_event(win32con.)
                #print(eul)
                global joy
                #print(cmdxyz*100)
                joy.set_cont_pov(2, toHexCmd(0.1+cmdxyz[1]))
                joy.set_cont_pov(1, toHexCmd(0.1+cmdxyz[0]))
                #


# wait for the heartbeat msg to find the system ID
# wait_heartbeat(master)
# master.wait_heartbeat()


master.recv()

proxy_8111_worker = proxy_8111()
t = threading.Thread(target=lambda :proccess_messages(master))
t1 = threading.Thread(target= proxy_8111_worker.run)
t2 = threading.Thread(target= lambda: start_wt_server(proxy_8111_worker,joy))

t.start()
t1.start()
t2.start()

with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()