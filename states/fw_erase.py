from application import Application
from programmers.programmer_factory import create_programmer
from . import State


class FirmwareEraseState(State):
    def __init__(self, app):
        super().__init__(app)
        self.is_error = False

    def do_step(self):
        for profile in self.app.profiles:
            p = create_programmer(self.app, profile)
            if not p.erase():
                self.is_error = True
                break
        return True

    def on_event(self, event):
        if self.is_error:
            return Application.APP_STATE_FAIL
        return Application.APP_STATE_SUCCESS
