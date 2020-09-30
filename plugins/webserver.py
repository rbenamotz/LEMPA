import json
import threading
import logging
from hardware import SERIAL_PORT
import serial
from flask import Flask, send_from_directory, jsonify, request
from flask_socketio import SocketIO, join_room, emit, send
from . import Plugin
import time

test_conf = {}
ser = None


def init_serial(speed):
    global ser
    try:
        ser = serial.Serial(port=SERIAL_PORT, baudrate=speed, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=0, writeTimeout=0)
        logging.info("Serial connection initiated with speed of " + str(speed))
    except:
        logging.warning(
            SERIAL_PORT + " not availabvle. Web Server will not be able to push data")


server = Flask(__name__)
server.debug = False
socketio = SocketIO(server)


def export_config():
    global ser
    if ser == None:
        raise Exception(
            "Serial not available. Can't push data. Try to enable Serial with raspi-config")
    packet = bytearray()
    log = ""
    for f in test_conf:
        i = int(f["value"])
        packet.append(i)
        if len(log) > 0:
            log = log + ","
        log = log + str(i)
    ser.write(packet)
    socketio.emit('serialout', log)


@server.route('/')
def root():
    return send_from_directory(".", "form.html")

@server.route('/data', methods=["GET"])
def data_get():
    return jsonify(test_conf)

@server.route('/data', methods=["POST"])
def data_post():
    data = request.get_json(force=True)
    for f in data:
        for f1 in test_conf:
            if f1["id"] == f["id"]:
                f1["value"] = f["value"]
    export_config()
    return ("Data (probably) sent to MCU")




class WebserverPlugin(Plugin):
    def __init__(self, app):
        self.cnt = 0
        super().__init__(app)

    def load_conf(self, conf):
        global test_conf
        init_serial(conf["serialSpeed"])
        test_conf = conf["fields"]

    def run(self):
        self.app.detail("Starting web server for serial injector on port 8080")
        socketio.run(server, host='0.0.0.0', port=8080)

    def serial_listener(self):
        ba = bytearray()
        while (ser == None):
            time.sleep(0.2)
        while True:
            b = ser.read()
            if b:
                ba.append(ord(b))
                if (b==b'\n'):
                    s = ba.decode("utf-8")
                    socketio.emit('serialin', s)
                    ba = bytearray()
            else:
                time.sleep(0.1)

    def on_start(self):
        daemon1 = threading.Thread(name='daemon_server', target=self.run)
        daemon1.setDaemon(True)
        daemon1.start()
        daemon2 = threading.Thread(name='serial_listener', target=self.serial_listener)
        daemon2.setDaemon(True)
        daemon2.start()
