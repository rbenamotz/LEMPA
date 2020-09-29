from application import Application
from . import State
from programmers.avr import avr
from programmers.esp import esp


class ProgramState(State):

    def __create_programmer__(self, profile):
        code = profile["programmer"]
        if code == 'linuxspi':
            return avr(self.app, profile)
        if code == 'esptool':
            return esp(self.app, profile)
        raise Exception("Unknown programmer of type {}".format(code))

    def __init__(self, app):
        super().__init__(app)
        self.is_error = False

    def do_step(self):
        for profile in self.app.profiles:
            p = self.__create_programmer__(profile)
            if not p.program():
                self.is_error = True
                break
        return True

    def on_event(self, event):
        if self.is_error:
            return Application.APP_STATE_FAIL
        return Application.APP_STATE_SUCCESS
