import tornado.ioloop
import tornado.web
import tornado.websocket
import time
import os
import pyvjoy
import json
from util import *

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class WTWebSocket(tornado.websocket.WebSocketHandler):

    def initialize(self, worker):
        print("Init WT handler")
        worker.ws = self
        self.worker = worker

    def open(self):
        print("WS Online")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")
        self.worker.ws = None

    def check_origin(self, origin):
        return True
class WTControlSocket(tornado.websocket.WebSocketHandler):

    def initialize(self, joy):
        print("Init Control handler")
        self.joy = joy

    def open(self):
        print("WS Control Online")

    def on_message(self, message):
        try:
            data = json.loads(message)
            #print("set throttle to {0}".format(data["throttle"]))
            th = (data["throttle"] / 100 - 0.5)*2
            self.joy.set_axis(pyvjoy.HID_USAGE_SL0, toHexCmd(th))
        except Exception as e:
            print("Recieve wrong message {0}".format(e))

    def on_close(self):
        print("Con WebSocket closed")

    def check_origin(self, origin):
        return True

def make_app(worker,joy):
    return tornado.web.Application([
        (r"/flight_info", WTWebSocket,{'worker':worker}),
        (r"/flight_control", WTControlSocket, {'joy': joy}),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': os.path.dirname(os.path.realpath(__file__))+'/ThunderDash/'}),
    ])

def start_wt_server(worker,joy):
    app = make_app(worker,joy)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()