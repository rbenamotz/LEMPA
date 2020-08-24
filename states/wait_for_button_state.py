import time

import RPi.GPIO as GPIO

from application import Application
from .state import State

GPIO_BUTTON = 17


class WaitForButtonState(State):
    def __init__(self, app):
        super().__init__(app)
        self.app.green_led_on = False
        self.app.ref_led_on = False
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.button_down_since = None
        self.next_state = Application.APP_STATE_PROGRAMMING
        self.btn_initial_state = not GPIO.input(GPIO_BUTTON)

    def do_step(self):
        is_btn_down = not GPIO.input(GPIO_BUTTON)
        if self.btn_initial_state:
            if is_btn_down:
                return False
            self.btn_initial_state = False
            return False
        if not self.button_down_since:
            if is_btn_down:
                self.button_down_since = time.time()
            return False

        if is_btn_down:
            t = time.time() - self.button_down_since
            if t > 2:
                self.next_state = Application.APP_STATE_PROFILE_SENSE
                return True
            return False
        return True

    def on_event(self, event):
        if event:
            return self.next_state
        return self
