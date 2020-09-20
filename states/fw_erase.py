import time

from application import Application
from states.state import State


class FirmwareEraseState(State):
    def __init__(self, app):
        super().__init__(app)

    def on_event(self, event):
        return Application.APP_STATE_SUCCESS

    def do_step(self):
        time.sleep(5)
        return True
