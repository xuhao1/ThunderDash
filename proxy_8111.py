import json
import urllib.request
from socket import *
import asyncio
import websockets
import time
import datetime


class proxy_8111:

    def __init__(self):
        self.msg = dict()
        self.map_bin = None
        self.tick = 0
        self.ws = None
        self.cs = socket(AF_INET, SOCK_DGRAM)
        self.cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.map_sent = False
        self.wt_online = False

    def refresh_from_8111(self):
        try:
            self.tick = self.tick + 1
            self.msg["indicator"] = json.loads(urllib.request.urlopen("http://127.0.0.1:8111/indicators").read())
            self.msg["state"] = json.loads(urllib.request.urlopen("http://127.0.0.1:8111/state").read())
            if self.tick % 500 == 1 or self.map_bin is None:
                self.map_bin = urllib.request.urlopen("http://127.0.0.1:8111/map.img").read()
                self.map_sent = False
                #time.sleep(0.01)
            self.wt_online = True
        except:
            self.wt_online = False

    def boardcast_udp(self):
        if self.wt_online:
            self.cs.sendto(json.dumps(self.msg).encode(), ('192.168.1.255', 58950))


    def boardcast_ws(self):
        if not(self.ws is None) and self.wt_online:
            self.ws.write_message(json.dumps(self.msg).encode())
            if not self.map_sent:
                print("sending map")
                self.map_sent = True
                self.ws.write_message(self.map_bin,True)

    def update(self):
        self.refresh_from_8111()
        self.boardcast_udp()
        self.boardcast_ws()
        time.sleep(0.01)

    def run(self):
        while True:
            self.update()