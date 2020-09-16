import importlib
import os
import re
import time

from application import Application
from states.state import State


class EnvInit(State):
    def __init__(self, app):
        super().__init__(app)
        self.steps_counter = 0

    def load_plugins(self):
        pysearchre = re.compile('.py$', re.IGNORECASE)
        pluginfiles = filter(pysearchre.search, os.listdir(os.path.join(os.path.dirname(__file__), '../plugins')))
        form_module = lambda fp: '.' + os.path.splitext(fp)[0]
        pp = map(form_module, pluginfiles)
        importlib.import_module('plugins')
        for plugin in pp:
            if not plugin.startswith('__'):
                module = importlib.import_module(plugin, package="plugins")
                class_ = getattr(module, "WebserverPlugin")
                instance = class_(self.app)
                instance.on_start()
                self.app.plugins.append(instance)

    def do_step(self):
        if self.steps_counter == 0:
            self.load_plugins()
        self.steps_counter = self.steps_counter + 1
        self.app.blue_led_on = (self.steps_counter % 3 == 0)
        self.app.green_led_on = (self.steps_counter % 3 == 1)
        self.app.red_led_on = (self.steps_counter % 3 == 2)
        if self.steps_counter >= 100:
            self.app.blue_led_on = False
            self.app.green_led_on = False
            self.app.red_led_on = False
            return True
        return False

    def on_event(self, event):
        return Application.APP_STATE_PROFILE_SENSE
