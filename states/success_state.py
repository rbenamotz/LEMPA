import time

from application import Application
from . import State


class SuccessState(State):
    def __init__(self, app):
        super().__init__(app)

    def on_event(self, event):
        return Application.APP_STATE_WAITING_FOR_BUTTON

    def do_step(self):
        time.sleep(3)
        return True
