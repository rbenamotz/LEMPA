import json
import os
import threading
import logging
from hardware import SERIAL_PORT
import serial
from flask import Flask, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit
from . import Plugin
import time
from views import View

test_conf = {}
ser = None
serial_speed = 9600


def init_serial():
    global ser
    try:
        ser = serial.Serial(port=SERIAL_PORT, baudrate=serial_speed, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=0, writeTimeout=0)
        logging.info(
            "Serial connection initiated with speed of " + str(serial_speed))
    except:
        logging.warning(
            SERIAL_PORT + " not availabvle. Web Server will not be able to push data")


server = Flask(__name__)
server.debug = False
socketio = SocketIO(server, cors_allowed_origin="*", log_output=False)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)


def export_config():
    global ser
    if ser == None:
        raise Exception(
            "Serial not available. Can't push data. Try to enable Serial with raspi-config")
    packet = bytearray()
    for f in test_conf:
        i = int(f["value"])
        packet.append(i)
    log = ','.join('0x{:02X}'.format(a) for a in packet)
    ser.write(packet)
    socketio.emit('serialout', log)

def export_text(txt):
    global ser
    if ser == None:
        raise Exception(
            "Serial not available. Can't push data. Try to enable Serial with raspi-config")
    ser.write(txt.encode());
    socketio.emit('serialout', txt)


@server.route('/')
def root():
    return send_from_directory(".", "index.html")

@server.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(server.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')


@server.route('/data', methods=["GET"])
def data_get():
    return jsonify(test_conf)


@server.route('/data', methods=["POST"])
def data_post():
    j = request.get_json(force=True)
    if (j["type"] == "form"):
        for f in j["data"]:
            for f1 in test_conf:
                if f1["id"] == f["id"]:
                    f1["value"] = f["value"]
        export_config()
    elif j["type"] == "text":
        export_text(j["data"])
    else:
        raise Exception ("Unknown type")
    return ("Data (probably) sent to MCU")


def update_serial_status():
    data = {"connected": (ser != None), "speed": serial_speed}
    socketio.emit('serialstatus', data)


class WebserverPlugin(Plugin, View):
    def __init__(self, app):
        self.cnt = 0
        super().__init__(app)

    def header(self):
        socketio.emit('viewHeader',self.app.app_state)

    def print(self, txt):
        socketio.emit('viewPrint', txt)

    def detail(self, txt):
        socketio.emit('viewDetail', txt)

    def error(self, e):
        socketio.emit('viewError', txt)

    def cleanup(self):
        pass

    def refresh(self):
        pass

    def load_conf(self, conf):
        global test_conf, serial_speed
        serial_speed = conf["serialSpeed"]
        test_conf = conf["fields"]

    def run(self):
        self.app.detail("Starting web server for serial injector on port 8080")
        socketio.run(server, host='0.0.0.0', port=8080)

    def serial_listener(self):
        global ser
        ba = bytearray()
        while True:
            try:
                if (ser == None):
                    update_serial_status()
                    ser = serial.Serial(port=SERIAL_PORT, baudrate=serial_speed, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS, timeout=0, writeTimeout=0)
                    logging.info(
                        "Serial connection initiated with speed of " + str(serial_speed))
                    while (ser == None):
                        time.sleep(0.2)
                    update_serial_status()
                b = ser.read()
                if b:
                    ba.append(ord(b))
                    if (b == b'\n'):
                        s = ba.decode("utf-8", errors='replace')
                        socketio.emit('serialin', s)
                        ba = bytearray()
                else:
                    time.sleep(0.1)
            except Exception as e:
                logging.error(e)
                if ser:
                    ser.close()
                    ser = None

    def on_start(self):
        daemon1 = threading.Thread(name='daemon_server', target=self.run)
        daemon1.setDaemon(True)
        daemon1.start()
        daemon2 = threading.Thread(
            name='serial_listener', target=self.serial_listener)
        daemon2.setDaemon(True)
        daemon2.start()
