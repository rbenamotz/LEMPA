import time

from application import Application
from . import State
from subprocess import call


class ShutDownState(State):
    def __init__(self, app):
        super().__init__(app)


    def do_step(self):
        time.sleep(1)
        call("sudo shutdown 1", shell=True)
        Application.should_exit = True
        return True
