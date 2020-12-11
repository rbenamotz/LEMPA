from application import Application
from programmers.programmer_factory import create_programmer
from . import State
from hardware import PIN_MASTER_POWER
import RPi.GPIO as GPIO


class ProgramState(State):
    def __init__(self, app):
        super().__init__(app)
        self.is_error = False

    def do_step(self):
        # GPIO.output(PIN_MASTER_POWER,True)
        for profile in self.app.profiles:
            p = create_programmer(self.app, profile)
            if not p.program():
                self.is_error = True
                break
        # GPIO.output(PIN_MASTER_POWER,False)
        return True

    def on_event(self, event):
        if self.is_error:
            return Application.APP_STATE_FAIL
        return Application.APP_STATE_SUCCESS
