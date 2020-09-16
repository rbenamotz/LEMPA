import subprocess

import RPi.GPIO as GPIO
import esptool

from application import Application
from states.state import State


class ProgramState(State):
    __STEP_INIT = 0
    __STEP_FUSE = 1
    __STEP_PROGRAM = 2
    __STEP_ESPTOOL = 3

    def __run_avrdude__(self, params):
        command = "/usr/bin/sudo avrdude {}".format(params)
        process = subprocess.Popen(command.split(), stderr=subprocess.PIPE)
        while True:
            output = process.stderr.readline()
            if len(output) == 0 and process.poll() is not None:
                break
            if output:
                self.app.print(output.strip().decode('utf-8'))
        rc = process.poll()
        self.is_error = (rc != 0)

    def __init__(self, app):
        super().__init__(app)
        self.step = self.__STEP_INIT
        self.app.blue_led_on = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.profile_index = 0
        self.programming_speed = 125000
        self.profile = None
        self.is_error = False

    def __do_step_init(self):
        self.app.app_state = Application.APP_STATE_PROGRAMMING
        self.profile = self.app.profiles[self.profile_index]
        if "speed" in self.profile:
            s = self.profile["speed"]
            self.programming_speed = s

    def __do_step_fuse(self):
        if not self.profile["programmer"] == 'linuxspi':
            return
        f = self.profile["fuses"]
        command: str = '-p {} -C ./avrdude_profile.conf -c linuxspi -P /dev/spidev0.0 -b {} ' \
                       '-D -e -u -U lfuse:w:{}:m -U hfuse:w:{}:m'.format(
            self.profile["device"], self.programming_speed, f["lfuse"], f["hfuse"])
        if "efuse" in f:
            command = '{} -U efuse:w:{}:m'.format(command, f["efuse"])
        if "lock" in f:
            command = '{} -U lock:w:{}:m'.format(command, f["lock"])
        self.__run_avrdude__(command)

    def __do_step_esptool(self):
        if not self.profile["programmer"] == "esptool":
            return
        command = ['--port', '/dev/serial0', '--baud', '921600', 'write_flash']
        for b in self.profile["bins"]:
            command.append(b["addr"])
            command.append("bins/%s.hex" % (b["name"]))
        esptool.main(command)

    def __do_step_write_flash(self):
        if not self.profile["programmer"] == "linuxspi":
            return
        b = self.profile["bins"][0]
        command: str = "-p %s -C ./avrdude_profile.conf -c linuxspi -P /dev/spidev0.0 -b %s -D -u -U flash:w:bins/%s.hex:i -u  -e " % (
            self.profile["device"], self.programming_speed, b["name"])
        self.__run_avrdude__(command)

    def do_step(self):
        if self.step == self.__STEP_INIT:
            self.__do_step_init()
        if self.step == self.__STEP_FUSE:
            self.app.print("Burning fuses")
            self.__do_step_fuse()
        if self.step == self.__STEP_PROGRAM:
            self.app.print("Programming")
            self.__do_step_write_flash()
        if self.step == self.__STEP_ESPTOOL:
            if self.profile["programmer"] == "esptool":
                self.app.print("Programming ESP. Sometimes it works")
                self.__do_step_esptool()
        # clean_results()
        self.step = self.step + 1
        if self.is_error:
            return True
        if self.step <= self.__STEP_ESPTOOL:
            return False
        self.profile_index = self.profile_index + 1
        if len(self.app.profiles) > self.profile_index:
            self.step = self.__STEP_INIT
            return False
        return True

    def on_event(self, event):
        if self.is_error:
            return Application.APP_STATE_FAIL
        return Application.APP_STATE_SUCCESS
