import time

from application import Application
from . import State
from subprocess import call
from hardware import PIN_BUTTON_PROG, PIN_BUTTON_ERASE
from .hat_button import SinglePinButton
WAIT_DURATION = 10

class ShutDownState(State):
    def __init__(self, app):
        super().__init__(app)
        self.count_down_start = time.time()
        self.last_print_time = 0
        self.button_prog = SinglePinButton("Prog", app, PIN_BUTTON_PROG)
        self.button_prog.on_short_click = self.__do_cancel

        self.button_erase = SinglePinButton("Erase", app, PIN_BUTTON_ERASE)
        self.button_erase.on_short_click = self.__do_cancel

    def __do_cancel(self):
        self.app.print("shutdown cancelled")
        #call ("sudo shutdown -c", shell=True)

    def do_step(self):
        if self.button_erase.loop() or self.button_prog.loop():
            return True
        t = int(time.time() - self.count_down_start)
        pt = WAIT_DURATION - t
        if pt==0:
            Application.should_exit = True
            call ("sleep 3 && sudo shutdown now &", shell=True)
            return True
        if self.last_print_time != pt:
            self.app.print("Shutdown in {}s".format(pt))
            self.last_print_time = pt
        return False

    def on_event(self, event):
        return Application.APP_STATE_PROFILE_SENSE
