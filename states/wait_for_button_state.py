from application import Application
from . import State
from hardware import PIN_BUTTON_PROG, PIN_BUTTON_ERASE
from .hat_button import HatButton



class WaitForButtonState(State):

    def __do_erase(self):
        self.next_state = Application.APP_STATE_ERASE

    def __do_prog(self):
        self.next_state = Application.APP_STATE_PROGRAMMING

    def __do_dowload(self):
        self.next_state = Application.APP_STATE_PROFILE_SENSE

    def __init__(self, app):
        super().__init__(app)
        self.button_prog = HatButton('Prog', app, PIN_BUTTON_PROG)
        self.button_prog.on_short_click = self.__do_prog
        self.button_prog.on_long_click = self.__do_dowload
        self.button_prog.long_click_action_name = "Download"

        self.button_erase = HatButton('Erase', app, PIN_BUTTON_ERASE)
        self.button_erase.long_click_action_name = "Erase"
        # self.button_erase.long_click_cancel_message = Application.APP_STATE_WAITING_FOR_BUTTON
        self.button_erase.on_long_click = self.__do_erase
        self.button_erase.long_click_duration = 3

        self.next_state = None

    def do_step(self):
        return self.button_erase.loop() or self.button_prog.loop()

    def on_event(self, event):
        if event:
            return self.next_state
        return self
