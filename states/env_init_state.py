import importlib
import logging
from os.path import exists
import re
import time
import RPi.GPIO as GPIO
from glob import glob
from hardware import SERIAL_PORT


from application import Application
from profiles import init_profile_data
from states import State
from hardware import PIN_ESP_RESET, PIN_MASTER_POWER


class EnvInit(State):
    def __init__(self, app):
        super().__init__(app)
        self.init_time = time.time()
        self.steps_counter = 0

    def __load_profiles__(self):
        init_profile_data(self.app)
    
    def __init_serial__(self):
        if not exists(SERIAL_PORT):
            logging.warn("Serial port {} does not exist. Please enable using raspi-conif".format(SERIAL_PORT))
            return
        self.app.serial_port = SERIAL_PORT

    def __load_plugins__(self):
        if len(self.app.plugins) > 0:
            logging.warning("Plugins already loaded. Not loading again")
            return

        def form_module(fp):
            output = fp.replace("/", ".")[2:]
            if (output.endswith(".")):
                output = output[0:len(output)-1]
            return output
        dirs = glob("./plugins/*/")
        for d in dirs:
            if d.startswith("./plugins/__"):
                continue
            module = importlib.import_module(".__init__", form_module(d))
            class_ = getattr(module, "LempaPlugin")
            instance = class_(self.app)
            instance.on_start()
            self.app.plugins.append(instance)

    def __read_hat_info_field__(self, field, default):
        try:
            f = open("/proc/device-tree/hat/" + field, "r")
            return f.read()
        except Exception:
            logging.warning(
                "Could not load HAT info for \"{}\". Defaulting to: \"{}\"".format(field, default))
            return default

    def __read_hat_info__(self):
        app_name = self.__read_hat_info_field__("product", "LEMPA")
        profiles_url = None
        if ("$$$" in app_name):
            p = app_name.index("$$$")
            profiles_url = app_name[p+3:]
            while profiles_url.endswith('\x00'):
                profiles_url = profiles_url[0:len(profiles_url) - 1]
            app_name = app_name[0:p]
        self.app.my_name = app_name
        self.app.profiles_url = profiles_url
        self.app.print(self.app.my_name)

    def __setup_pins__(self):
        GPIO.setup(PIN_ESP_RESET, GPIO.OUT)
        GPIO.output(PIN_ESP_RESET, True)
        GPIO.setup(PIN_MASTER_POWER, GPIO.OUT)
        GPIO.output(PIN_MASTER_POWER, True)

    def do_step(self):
        if self.steps_counter == 1:
            self.__read_hat_info__()
        if self.steps_counter == 2:
            self.__load_profiles__()
        if self.steps_counter == 3:
            self.__init_serial__()
        if self.steps_counter == 4:
            self.__load_plugins__()
        if self.steps_counter == 5:
            self.__setup_pins__()
        self.steps_counter = self.steps_counter + 1
        t = time.time() - self.init_time
        return (self.steps_counter > 5 and t > 2)

    def on_event(self, event):
        return Application.APP_STATE_PROFILE_SENSE
