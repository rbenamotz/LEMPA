from application import Application
from . import State
from hardware import PIN_BUTTON_PROG, PIN_BUTTON_ERASE
from .hat_button import SinglePinButton


class ExceptionState(State):
    def __do_acknloedge(self):
        self.is_acknowledged = True

    def __init__(self, app):
        super().__init__(app)
        self.is_acknowledged = False
        self.button_prog = SinglePinButton("Ack", app, PIN_BUTTON_PROG)
        self.button_prog.on_short_click = self.__do_acknloedge

        self.button_erase = SinglePinButton("Erase", app, PIN_BUTTON_ERASE)
        self.button_erase.long_click_action_name = "Ack"
        self.button_erase.on_short_click = self.__do_acknloedge

    def do_step(self):
        return self.button_erase.loop() or self.button_prog.loop()

    def on_event(self, event):
        return Application.APP_STATE_PROFILE_SENSE
