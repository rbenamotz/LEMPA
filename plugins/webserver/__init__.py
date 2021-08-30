from application import Application
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


logging.getLogger("socketio").setLevel(logging.ERROR)
logging.getLogger("engineio").setLevel(logging.ERROR)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


class LempaPlugin(Plugin, View):
    def __init__(self, app):
        super().__init__(app)
        self.serial_daemon = None
        self.app = app
        self.cnt = 0
        self.server = Flask(__name__)
        self.server.debug = False
        self.server.add_url_rule("/", "root", self.root)
        self.server.add_url_rule(
            "/data", "data_get", self.data_get, methods=["GET"])
        self.server.add_url_rule("/data", "data_post",
                                 self.data_post, methods=["POST"])
        self.server.add_url_rule("/prgm", "btn_prgm",
                                 self.btn_prgm, methods=["POST"])
        self.server.add_url_rule("/favicon.ico", "favicon", self.favicon)
        self.socketio = SocketIO(
            self.server, cors_allowed_origin="*", log_output=False)

    def header(self):
        if (self.serial_daemon):
            self.serial_daemon.state_changed(self.app.app_state)
        self.socketio.emit("viewHeader", self.app.app_state)

    def print(self, txt):
        self.socketio.emit("viewPrint", txt)

    def detail(self, txt):
        self.socketio.emit("viewDetail", txt)

    def error(self, e):
        self.socketio.emit("viewError", str(e))

    def cleanup(self):
        pass

    def set_profile_name(self, x):
        self.socketio.emit("viewProfile", x)

    def load_conf(self, conf):
        global test_conf, serial_speed
        serial_speed = conf["serialSpeed"]
        test_conf = conf["fields"]
        close_serial()

    def run(self):
        self.app.detail(
            "LEMPA Web Interface on port {}".format(WEB_SERVER_PORT))
        self.socketio.run(self.server, host="0.0.0.0", port=WEB_SERVER_PORT)

    def on_start(self):
        self.serial_daemon = SerialConnectionThread(self.serial_in, self.update_serial_status)
        daemon1 = threading.Thread(name="daemon_server", target=self.run)
        daemon1.setDaemon(True)
        daemon1.start()
        daemon2 = threading.Thread(name="serial_listener", target=self.serial_daemon.run)
        daemon2.setDaemon(True)
        daemon2.start()

    def data_get(self):
        output = {}
        output["header"] = self.app.app_state
        output ["profile"] = self.app.profile_info
        output["binData"] = test_conf
        return jsonify(output)

    def serial_in(self, s):
        self.socketio.emit("serialin", s)

    def update_serial_status(self):
        data = {"connected": (ser is not None), "speed": serial_speed}
        self.socketio.emit("serialstatus", data)

    def root(self):
        return send_from_directory("./static", "index.html")

    def btn_prgm(self):
        self.app.move_to_state = Application.APP_STATE_PROGRAMMING
        return "ok"

    def data_post(self):
        j = request.get_json(force=True)
        if j["type"] == "form":
            for f in j["data"]:
                for f1 in test_conf:
                    if f1["id"] == f["id"]:
                        f1["value"] = f["value"]
            export_config(test_conf)
            log = ",".join("0x{:02X}".format(a)
                           for a in map(lambda x: int(x["value"]), test_conf))
            self.socketio.emit("serialout", log)
        elif j["type"] == "text":
            txt = j["data"]
            export_text(txt)
            self.socketio.emit("serialout", txt)
        else:
            raise ValueError("Unknown type")
        return "Data (probably) sent to MCU"

    def favicon(self):
        return send_from_directory(
            os.path.join(self.server.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )
