import importlib
import logging
import os
import re
import time
import RPi.GPIO as GPIO


# Loox Programmer 0.3$$$https://84exaczpag.execute-api.us-east-1.amazonaws.com/public/profiles
from application import Application
from profiles import init_profile_data
from states import State
from hardware import PIN_ESP_RESET


class EnvInit(State):
    def __init__(self, app):
        super().__init__(app)
        self.init_time = time.time()
        self.steps_counter = 0
    
    def __load_profiles__(self):
        init_profile_data(self.app)

    def __load_plugins__(self):
        if len(self.app.plugins) > 0:
            logging.warning("Plugins already loaded. Not loading again")
            return
        pysearchre = re.compile(".py$", re.IGNORECASE)
        pluginfiles = filter(
            pysearchre.search,
            os.listdir(os.path.join(os.path.dirname(__file__), "../plugins")),
        )

        def form_module(fp):
            return "." + os.path.splitext(fp)[0]

        pp = map(form_module, pluginfiles)
        importlib.import_module("plugins")
        for plugin in pp:
            if not plugin.startswith(".__"):
                module = importlib.import_module(plugin, package="plugins")
                class_ = getattr(module, "WebserverPlugin")
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
        GPIO.output(PIN_ESP_RESET, False)

    def do_step(self):
        if self.steps_counter == 1:
            self.__read_hat_info__()
        if self.steps_counter == 2:
            self.__load_profiles__()
        if self.steps_counter == 3:
            self.__load_plugins__()
        if self.steps_counter == 4:
            self.__setup_pins__()
        self.steps_counter = self.steps_counter + 1
        t = time.time() - self.init_time
        return t > 2

    def on_event(self, event):
        return Application.APP_STATE_PROFILE_SENSE
