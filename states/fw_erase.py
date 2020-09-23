import time
import subprocess

from application import Application
from . import State

class FirmwareEraseState(State):
    def __init__(self, app):
        super().__init__(app)
        self.is_error = False
        self.profile = self.app.profiles[0]
        self.erase_speed = 125000
        if "speed" in self.profile:
            s = self.profile["speed"]
            self.erase_speed = s

    def __run_avrdude__(self, params):
        command = "/usr/bin/sudo avrdude {}".format(params)
        process = subprocess.Popen(command.split(), stderr=subprocess.PIPE)
        while True:
            output = process.stderr.readline()
            if len(output) == 0 and process.poll() is not None:
                break
            if output:
                self.app.detail(output.strip().decode('utf-8'))
        rc = process.poll()
        self.is_error = (rc != 0)

    def on_event(self, event):
        if self.is_error:
            return Application.APP_STATE_FAIL
        return Application.APP_STATE_SUCCESS

    def do_step(self):
        if not self.profile["programmer"] == "linuxspi":
            return True
        command: str = "-p %s -C ./avrdude_profile.conf -c linuxspi -P /dev/spidev0.0 -b %s -e" % (self.profile["device"], self.erase_speed)
        self.app.detail(command)
        self.__run_avrdude__(command)
        time.sleep(2)
        return True
