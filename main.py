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
        pygame.init()
        pygame.joystick.init()

        self.t16000m = None
        self.master = None
        self.cmdpov = None

        for k in range(pygame.joystick.get_count()):
            if pygame.joystick.Joystick(k).get_name() == "T.16000M":
                self.t16000m = pygame.joystick.Joystick(k)
        if self.t16000m is None:
            print("No t16000m found")
        else:
            self.t16000m.init()
            print("Found Joystick {0}".format(self.t16000m.get_name()))

        self.q_base = None
        self.vjoy = pyvjoy.VJoyDevice(1)
        self.proxy_8111_worker = proxy_8111()

        self.pov_x_offset = 0
        self.pov_y_offset = 0

        try:
            self.master = mavutil.mavlink_connection("COM3", baud="230400")
            print("Link to COM3 with mavlink")
        except:
            print("No master Found")
            self.master = None

    def on_press(self, key):
        if key == Key.f9:
            print("reset joystick pov")
            self.q_base = None

    def set_pov(self, x, y):
        self.vjoy.set_cont_pov(2, toHexCmd(0.1 + y + self.pov_y_offset))
        self.vjoy.set_cont_pov(1, toHexCmd(0.1 + x + self.pov_x_offset))

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

    def process_pov_quat(self,quat):
        q_now = QuaternionBase(attitude=quat)
        if self.q_base is None:
            self.q_base = q_now.inversed
        q_now = self.q_base.__mul__(q_now)
        eul = q_now.euler* 180 / 3.14
        #print(eul)
        #print(eul)
        if self.cmdpov is None:
            self.cmdpov = eul / 180
        else:
            # A naive lowpass filter
            self.cmdpov = eul / 180 * 0.4 + self.cmdpov * 0.6
        self.set_pov(-self.cmdpov[2], self.cmdpov[1])

    def update_from_external_joy(self):
        pygame.event.get()
        if self.t16000m is None:
            return
        # print(self.t16000m.get_hat(0))
        # print(self.t16000m.get_axis(0))
        self.pov_x_offset, self.pov_y_offset = self.t16000m.get_hat(0)
        self.pov_x_offset = -self.pov_x_offset *0.2
        self.pov_y_offset = self.pov_y_offset *0.2

    def main_thread(self):
        if not (self.master is None):
            print("recieve master")
            self.master.recv()
        while True:
            #print("refresh")
            if not (self.master is None):
                self.update_from_mavlink()
            else:
                time.sleep(0.01)
            self.update_from_external_joy()

    def run(self):
        print("Run....")
        self.th0 = threading.Thread(target=self.proxy_8111_worker.run)
        self.th1 = threading.Thread(target=lambda: start_wt_server(self))
        self.th2 = threading.Thread(target=self.main_thread)
        self.th0.start()
        self.th1.start()
        self.th2.start()
        with Listener(
                on_press=lambda x: self.on_press(x)) as listener:
            listener.join()


aircraft_con = game_aircraft_control()
aircraft_con.run()
