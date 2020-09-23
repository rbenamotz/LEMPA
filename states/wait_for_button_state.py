import time

import RPi.GPIO as GPIO

from application import Application
from . import State
from hardware import PIN_BUTTON_PROG, PIN_BUTTON_ERASE


class HatButton:
    def __init__(self, name, app, pin):
        self.name = name
        self.app = app
        self.pin = pin
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.button_down_since = None
        self.is_down = False
        self.last_print_time = 0
        self.long_click_action_name = None
        self.long_click_cancel_message = "Cancelled"
        self.on_long_click = None
        self.on_short_click = None
        self.long_click_duration = 3

    def __check_long_click(self):
        if not self.on_long_click:
            return False
        if not self.button_down_since and self.is_down:
            self.button_down_since = time.time()
            return False
        if not self.button_down_since:
            return False
        if not self.is_down:
            self.app.detail(self.name + " cancelled")
            self.last_print_time = 0
            self.app.print(self.long_click_cancel_message)
            self.button_down_since = None
            return False
        t = int(time.time() - self.button_down_since)
        delay_before_long_click_message = 0
        if self.on_short_click:
            delay_before_long_click_message = 0.2
        if t < self.long_click_duration:
            if t >= delay_before_long_click_message:
                pt = self.long_click_duration - t
                if self.long_click_action_name and self.last_print_time != pt:
                    self.app.print(
                        self.long_click_action_name + "? " + str(pt))
                    self.last_print_time = pt
            return False
        self.on_long_click()
        return True
        # self.next_state = Application.APP_STATE_ERASE
        # return True

    def __check_short_click(self):
        if not self.on_short_click:
            return False
        if self.button_down_since and not self.is_down:
            self.on_short_click()
            return True
        return False

    def loop(self):
        self.is_down = not GPIO.input(self.pin)
        if (self.__check_short_click()):
            return True
        return self.__check_long_click()


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
        self.button_erase.long_click_cancel_message = Application.APP_STATE_WAITING_FOR_BUTTON
        self.button_erase.on_long_click = self.__do_erase
        self.button_erase.long_click_duration = 5

        self.next_state = None

    def do_step(self):
        return self.button_erase.loop() or self.button_prog.loop()

    def on_event(self, event):
        if event:
            return self.next_state
        return self
