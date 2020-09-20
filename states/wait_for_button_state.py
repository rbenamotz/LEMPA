import time

import RPi.GPIO as GPIO

from application import Application
from .state import State

GPIO_BUTTON_PROG = 17
GPIO_BUTTON_ERASE = 27

class WaitForButtonState(State):
    def __init__(self, app):
        super().__init__(app)
        self.app.green_led_on = False
        self.app.ref_led_on = False
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BUTTON_PROG, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(GPIO_BUTTON_ERASE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.button_prog_down_since = None
        self.button_erase_down_since = None
        self.next_state = Application.APP_STATE_PROGRAMMING
        self.btn_prog_initial_state = not GPIO.input(GPIO_BUTTON_PROG)
        self.last_print_time = 0

    def do_step(self):
        is_btn_prog_down = not GPIO.input(GPIO_BUTTON_PROG)
        is_btn_erase_down = not GPIO.input(GPIO_BUTTON_ERASE)
        if self.btn_prog_initial_state:
            if is_btn_prog_down:
                return False
            self.btn_prog_initial_state = False
            return False
        if not self.button_prog_down_since and is_btn_prog_down:
            self.button_prog_down_since = time.time()
            return False
        if not self.button_erase_down_since and is_btn_erase_down:
            self.button_erase_down_since = time.time()
            return False
            
        if self.button_prog_down_since:
            if is_btn_prog_down:
                t = time.time() - self.button_prog_down_since
                if (t > 2):
                    self.next_state = Application.APP_STATE_PROFILE_SENSE
                    return True
            else:
                self.next_state = Application.APP_STATE_PROGRAMMING
                return True

        if self.button_erase_down_since:
            if not is_btn_erase_down:
                self.app.detail ("Erase cancelled")
                self.last_print_time = 0
                self.app.print(Application.APP_STATE_WAITING_FOR_BUTTON)
                self.button_erase_down_since = None
                return False
                
            t = int (time.time() - self.button_erase_down_since)
            if (t < 5):
                pt = 5 - t
                if self.last_print_time != pt:
                    self.app.print ("Erase? " + str(pt))
                    self.last_print_time = pt
                return False
            self.next_state = Application.APP_STATE_ERASE
            return True
        return False

    def on_event(self, event):
        if event:
            return self.next_state
        return self
