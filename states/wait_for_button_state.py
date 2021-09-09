import RPi.GPIO as GPIO
from hardware import PINS_PROFILES
from application import Application
from . import State
from hardware import PIN_BUTTON_PROG, PIN_BUTTON_ERASE, PIN_RESET_ATMEGA
from .hat_button import SinglePinButton, DoublePinButton
import time


class WaitForButtonState(State):
    def _do_erase(self):
        self.next_state = Application.APP_STATE_ERASE

    def _do_prog(self):
        self.next_state = Application.APP_STATE_PROGRAMMING

    def _do_dowload(self):
        self.next_state = Application.APP_STATE_PROFILE_SENSE

    def _do_shutdown(self):
        self.next_state = Application.APP_STATE_SHUTDOWN

    def __init__(self, app):
        super().__init__(app)
        self.watch_jumper = None
        if not self.app.skip_detect and "jumper" in self.app.profile_info:
            self.watch_jumper = self.app.profile_info["jumper"]
        self.waiting_for_board_disconnect = False
        if self.app.is_auto_detect:
            self.app.detail("Auto detect enabled")
            self.app.print("Connect MCU")
            GPIO.setup(PIN_RESET_ATMEGA, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.waiting_for_board_disconnect = True
        self.button_shut_down = DoublePinButton("Shutdown", app, PIN_BUTTON_PROG, PIN_BUTTON_ERASE)
        self.button_shut_down.on_long_click = self._do_shutdown
        self.button_shut_down.long_click_action_name = "Shut down"
        self.button_shut_down.long_click_duration = 5

        self.button_prog = SinglePinButton("Prog", app, PIN_BUTTON_PROG)
        self.button_prog.on_short_click = self._do_prog
        self.button_prog.on_long_click = self._do_dowload
        self.button_prog.long_click_action_name = "Download"

        self.button_erase = SinglePinButton("Erase", app, PIN_BUTTON_ERASE)
        self.button_erase.long_click_action_name = "Erase"
        self.button_erase.on_long_click = self._do_erase
        self.button_erase.long_click_duration = 3
        self.next_state = None

    def is_jumper_changed(self):
        if not self.watch_jumper:
            return False
        return GPIO.input(PINS_PROFILES[self.watch_jumper-1])


    def do_step(self):
        if self.is_jumper_changed():
            self.next_state = Application.APP_STATE_PROFILE_SENSE
            return True
        if self.button_shut_down.loop():
            return True
        if self.button_shut_down.is_down:
            self.button_erase.long_click_started = False
            self.button_prog.long_click_started = False
            return False
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
