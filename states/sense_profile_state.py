import sys
import time

import RPi.GPIO as GPIO

from application import Application, COMMAND_LINE_PARAM_PROFILE_ID
from profiles import profile_by_id, profile_by_jumper
from .state import State

PINS = [5, 6, 13, 19]


class SensingProfileState(State):
    def __load_profile__(self, profile_id, first=True):
        self.app.red_led_on = False
        p = profile_by_id(profile_id)
        if first:
            self.app.profiles = []
            self.app.profile_name = profile_id
            self.app.detail("Loading \"{}\"".format(profile_id))
            if "plugins" in p:
                for pl in self.app.plugins:
                    pl.load_conf(p["plugins"][0]["conf"])
        if p["type"] == "bin":
            self.app.profiles.append(p)
            return True
        if p["type"] == "composite":
            for p0 in p["profiles"]:
                self.__load_profile__(p0, False)
            return True
        raise Exception("Unknown profile type {}".format(p["type"]))

    def __init__(self, app):
        super().__init__(app)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for p in PINS:
            GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.skip_detect = False
        self.led_status = True
        if len(sys.argv) >= COMMAND_LINE_PARAM_PROFILE_ID + 1:
            id = sys.argv[COMMAND_LINE_PARAM_PROFILE_ID]
            if not id == '_':
                self.app.detail("Using profile from command line: {}".format(id))
                self.__load_profile__(sys.argv[1])
                self.skip_detect = True
                return
        self.app.detail("Detecting profile by jumper")
        self.message_shown = False

    def do_step(self):
        if self.skip_detect:
            return True
        for j in range(4):
            p = PINS[j]
            if not GPIO.input(p):
                self.app.detail("Detected jumper {}".format(j + 1))
                temp = profile_by_jumper(j + 1)
                id = temp["id"]
                self.__load_profile__(id)
                return True
        self.app.red_led_on = self.led_status
        self.led_status = not self.led_status
        time.sleep(0.1)
        if not self.message_shown:
            self.app.print("Connect jumper")
            self.message_shown = True
        return False

    def on_event(self, event):
        if event:
            return Application.APP_STATE_FIRMWARE_DOWNLOAD
        return self
