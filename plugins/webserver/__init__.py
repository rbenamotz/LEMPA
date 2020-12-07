import os
import threading
import logging
from flask import Flask, send_from_directory, jsonify, request
from serial.serialutil import SerialException
from flask_socketio import SocketIO
from .. import Plugin
import time
from views import View
from .SerialConnectionThread import close_serial, SerialConnectionThread, ser, serial_speed, export_text, export_config

test_conf = {}
WEB_SERVER_PORT = 8080


server = Flask(__name__)
server.debug = False
socketio = SocketIO(server, cors_allowed_origin="*", log_output=False)
logging.getLogger("socketio").setLevel(logging.ERROR)
logging.getLogger("engineio").setLevel(logging.ERROR)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


@server.route("/")
def root():
    return send_from_directory("./static", "index.html")


@server.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(server.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@server.route("/data", methods=["GET"])
def data_get():
    return jsonify(test_conf)


@server.route("/data", methods=["POST"])
def data_post():
    j = request.get_json(force=True)
    if j["type"] == "form":
        for f in j["data"]:
            for f1 in test_conf:
                if f1["id"] == f["id"]:
                    f1["value"] = f["value"]
        export_config(test_conf)
        socketio.emit("serialout", test_conf["data"])
    elif j["type"] == "text":
        txt = j["data"]
        export_text(txt)
        socketio.emit("serialout", txt)
    else:
        raise ValueError("Unknown type")
    return "Data (probably) sent to MCU"



def serial_in(s):
    socketio.emit("serialin", s)

def update_serial_status():
    data = {"connected": (ser is not None), "speed": serial_speed}
    socketio.emit("serialstatus", data)





class LempaPlugin(Plugin, View):
    def __init__(self, app):
        self.cnt = 0
        super().__init__(app)

    def header(self):
        socketio.emit("viewHeader", self.app.app_state)

    def print(self, txt):
        socketio.emit("viewPrint", txt)

    def detail(self, txt):
        socketio.emit("viewDetail", txt)

    def error(self, e):
        socketio.emit("viewError", str(e))

    def cleanup(self):
        pass

    def set_profile_name(self, x):
        socketio.emit("viewProfile", x)

    def load_conf(self, conf):
        global test_conf, serial_speed
        serial_speed = conf["serialSpeed"]
        test_conf = conf["fields"]
        close_serial()

    def run(self):
        self.app.detail(
            "LEMPA Web Interface on port {}".format(WEB_SERVER_PORT))
        socketio.run(server, host="0.0.0.0", port=WEB_SERVER_PORT)

    def on_start(self):
        t = SerialConnectionThread(serial_in,update_serial_status)
        daemon1 = threading.Thread(name="daemon_server", target=self.run)
        daemon1.setDaemon(True)
        daemon1.start()
        daemon2 = threading.Thread(
            name="serial_listener", target=t.run)
        daemon2.setDaemon(True)
        daemon2.start()
