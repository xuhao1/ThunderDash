from pymavlink import mavutil
from pymavlink.quaternion import *
import sys
import math
import pyvjoy
import threading
from proxy_8111 import proxy_8111
from wt_server import *
from util import *
import pygame
from pynput.keyboard import Key, Listener

class game_aircraft_control:
    def __init__(self):

        self.master = None
        self.cmdpov = None

        self.init_external_joys()
        self.q_base = None
        self.vjoy = pyvjoy.VJoyDevice(1)
        self.proxy_8111_worker = proxy_8111()

        self.pov_x_offset = 0
        self.pov_y_offset = 0
        self.zoom = 0
        self.zoom_base_quat = None
        self.zoom_base_povx = 0
        self.zoom_base_povy = 0
        self.zoom_on_press = False
        self.indicator = None
        self.state = None

        self.roll_trim = 0
        self.aileron = 0
        try:
            self.master = mavutil.mavlink_connection("COM3", baud="230400")
            print("Link to COM3 with mavlink")
        except Exception as e:
            print("No master Found {0}".format(e))
            self.master = None

    def init_external_joys(self):
        pygame.init()
        pygame.joystick.init()
        self.t16000m = None
        self.twcs = None
        for k in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(k)
            if joystick.get_name() == "T.16000M":
                self.t16000m = pygame.joystick.Joystick(k)
                self.t16000m.init()
                print("Found Joystick {0}".format(self.t16000m.get_name()))

            if joystick.get_name() == "TWCS Throttle":
                self.twcs = joystick
                self.twcs.init()
                print("Found Joystick {0}".format(self.twcs.get_name()))

        if self.t16000m is None:
            print("No t16000m found")

    def on_press(self, key):
        if key == Key.f9:
            print("reset joystick pov")
            self.q_base = None

    def set_pov(self, x, y):
        self.vjoy.set_cont_pov(2, toHexCmd(0.1 + y + self.pov_y_offset))
        self.vjoy.set_cont_pov(1, toHexCmd(0.1 + x + self.pov_x_offset))

    def set_zoom(self, zoom):
        # zoom 0-1
        self.vjoy.set_axis(pyvjoy.HID_USAGE_SL1, toHexCmd((zoom - 0.5) * 2))
        return

    def get_POVXYZ_from_quat(self, quat):
        eul = quat.euler * 180 / 3.14
        cmd = eul / 180
        v = quat.transform(np.array([1, 0, 0]))
        # print(v)
        yang = - math.asin(v[2])
        cmd[1] = yang
        # print(yang/3.14)
        return cmd

    def update_from_mavlink(self):
        if self.master is None:
            return
        msg = self.master.recv_match(blocking=True)
        if not msg:
            return
        if msg.get_type() == "BAD_DATA":
            return
        else:
            if msg._type == "ATTITUDE_QUATERNION":
                quat = [msg.q1, msg.q2, msg.q3, msg.q4]
                self.process_pov_quat(quat)

    def process_pov_quat(self, quat):
        q_now = QuaternionBase(attitude=quat)
        if self.q_base is None:
            self.q_base = q_now.inversed
        if self.zoom == 0 or self.zoom_base_quat is None:
            self.zoom_base_quat = q_now.inversed

        cmd = None
        if self.zoom == 0:
            q_now = self.q_base.__mul__(q_now)
            q_now.normalize()
            cmd = self.get_POVXYZ_from_quat(q_now)
            cmd[2] = cmd[2] * 10
            cmd[1] = cmd[1] * 1
            self.zoom_base_povx = cmd[2]
            self.zoom_base_povy = cmd[1]
        else:
            q_now = self.zoom_base_quat.__mul__(q_now)
            cmd = self.get_POVXYZ_from_quat(q_now)
            cmd[2] = cmd[2] * 2.0 + self.zoom_base_povx
            cmd[1] = cmd[1] * 0.4 + self.zoom_base_povy
            pass

        if self.cmdpov is None:
            self.cmdpov = cmd
        else:
            # A naive lowpass filter
            self.cmdpov = cmd * 0.4 + self.cmdpov * 0.6

        self.cmdpov[2] = - self.cmdpov[2]
        # print(self.cmdpov)
        self.set_pov(self.cmdpov[2], self.cmdpov[1])

    def update_from_external_joy(self):
        pygame.event.get()
        if self.t16000m is None and self.twcs is None:
            return
        self.pov_x_offset, self.pov_y_offset = self.t16000m.get_hat(0)
        if not (self.twcs is None):
            _, trimrollbtn = self.twcs.get_hat(0)
            self.roll_trim = self.roll_trim - trimrollbtn * 0.05
            pass

        # self.pov_x_offset, self.pov_y_offset = self.twcs.get_axis(0),-self.twcs.get_axis(1)
        self.pov_x_offset = -self.pov_x_offset * 0.4
        self.pov_y_offset = self.pov_y_offset * 0.2

        if self.t16000m.get_button(1) > 0:
            if not self.zoom_on_press:
                self.zoom = 1 - self.zoom
            self.zoom_on_press = True
        else:
            self.zoom_on_press = False
        if self.t16000m.get_button(9) > 0:
            self.q_base = None

        self.set_aileron(self.t16000m.get_axis(0))

        self.set_zoom(self.zoom)

    def set_aileron(self,v):
        v = JoyEXP(v,1) + self.roll_trim / 100
        self.vjoy.set_axis(pyvjoy.HID_USAGE_X, toHexCmd(v))
        pass

    def main_thread(self):
        if not (self.master is None):
            print("recieve master")
            self.master.recv()
        while True:
            # print("refresh")
            if not (self.master is None):
                self.update_from_mavlink()
            else:
                time.sleep(0.01)
            self.update_from_external_joy()

            self.indicator = self.proxy_8111_worker.msg["indicator"]
            self.state = self.proxy_8111_worker.msg["state"]

    def get_roc(self):
        try:
            return self.indicator["vario"]
        except:
            return math.nan
    def run(self):
        print("Run....")
        self.th0 = threading.Thread(target=self.proxy_8111_worker.run)
        self.th1 = threading.Thread(target=lambda: start_wt_server(self))
        self.th2 = threading.Thread(target=self.main_thread)
        self.th0.start()
        self.th1.start()
        self.th2.start()
        # with Listener(
        #         on_press=lambda x: self.on_press(x)) as listener:
        #     listener.join()

