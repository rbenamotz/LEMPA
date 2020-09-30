import json
import threading
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from hardware import *
import serial

from . import Plugin

test_conf = {}
ser = None


def init_serial(speed):
    global ser
    try:
        ser = serial.Serial(port=SERIAL_PORT, baudrate=speed, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=0, writeTimeout=0)
        print("Serial connection initiated with speed of ", speed)
    except:
        logging.warning(
            SERIAL_PORT + " not availabvle. Web Server will not be able to push data")


class MyRequestHandler(BaseHTTPRequestHandler):
    @staticmethod
    def export_config():
        if ser == None:
            raise Exception("Serial not available. Can't push data. Try to enable Serial with raspi-config")
        packet = bytearray()
        for f in test_conf:
            packet.append(int(f["value"]))
        ser.write(packet)

    def do_get_data(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        message = json.dumps(test_conf)
        self.wfile.write(bytes(message, "utf8"))

    def log_message(self, format, *args):
        return

    def do_POST(self):
        global test_conf
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf8'))
        for f in data:
            for f1 in test_conf:
                if f1["id"] == f["id"]:
                    f1["value"] = f["value"]
        try:
            self.export_config()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes("Data sent to system. Maybe", "utf8"))
        except Exception as e:
            logging.error(e)
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(str(e), "utf8"))
        return

    def do_GET(self):
        if self.path == "/data":
            return self.do_get_data()
        f = open('plugins/form.html', 'r')
        message = f.read()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))
        return


class WebserverPlugin(Plugin):
    def __init__(self, app):
        super().__init__(app)

    def load_conf(self, conf):
        global test_conf
        init_serial(conf["serialSpeed"])
        test_conf = conf["fields"]

    def run(self):
        # return
        self.app.detail("Starting web server for serial injector on port 8080")
        httpd = HTTPServer(('', 8080), MyRequestHandler)
        httpd.serve_forever()

    def on_start(self):
        daemon = threading.Thread(name='daemon_server', target=self.run)
        daemon.setDaemon(True)
        daemon.start()
