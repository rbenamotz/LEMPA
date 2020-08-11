import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import serial

from plugin import Plugin

test_conf = {}
ser = serial.Serial(port='/dev/serial0', baudrate=38400, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS, timeout=0, writeTimeout=0)


class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    def export_config(self):
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
        test_conf = data;
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.export_config()
        self.wfile.write(bytes("Data sent to system. Maybe", "utf8"))
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
        test_conf = conf["fields"]

    def run(self):
        self.app.print("Starting web server for serial injector on port 8080")
        httpd = HTTPServer(('', 8080), testHTTPServer_RequestHandler)
        httpd.serve_forever()

    def on_start(self):
        daemon = threading.Thread(name='daemon_server', target=self.run)
        daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()