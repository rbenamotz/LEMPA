import RPi.GPIO as GPIO
from application import Application
from . import State
from hardware import PIN_BUTTON_PROG, PIN_BUTTON_ERASE, PIN_RESET_ATMEGA
from .hat_button import HatButton
import time


class WaitForButtonState(State):

    def _do_erase(self):
        self.next_state = Application.APP_STATE_ERASE

    def _do_prog(self):
        self.next_state = Application.APP_STATE_PROGRAMMING

    def _do_dowload(self):
        self.next_state = Application.APP_STATE_PROFILE_SENSE

    def __init__(self, app):
        super().__init__(app)
        self.waiting_for_board_disconnect = False
        if self.app.is_auto_detect:
            self.app.detail("Auto detect enabled")
            self.app.print("Connect MCU")
            GPIO.setup(PIN_RESET_ATMEGA, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.waiting_for_board_disconnect = True
        self.button_prog = HatButton('Prog', app, PIN_BUTTON_PROG)
        self.button_prog.on_short_click = self._do_prog
        self.button_prog.on_long_click = self._do_dowload
        self.button_prog.long_click_action_name = "Download"

        self.button_erase = HatButton('Erase', app, PIN_BUTTON_ERASE)
        self.button_erase.long_click_action_name = "Erase"
        self.button_erase.on_long_click = self._do_erase
        self.button_erase.long_click_duration = 3

        self.next_state = None
    

    def do_step(self):
        if self.button_erase.loop() or self.button_prog.loop():
            return True
        if self.waiting_for_board_disconnect:
            if not GPIO.input(PIN_RESET_ATMEGA):
                self.waiting_for_board_disconnect = False
            return False

        if self.app.is_auto_detect:
            b = GPIO.input(PIN_RESET_ATMEGA)
            if b:
                self.app.print("Chip detected")
                time.sleep(1)
                self._do_prog()
                return True
        return False

    def on_event(self, event):
        if event:
            return self.next_state
        return self
