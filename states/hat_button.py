import logging
import RPi.GPIO as GPIO
import time


class HatButton:
    def __init__(self, name, app):
        self.name = name
        self.app = app
        self.button_down_since = None
        self.is_down = False
        self.last_print_time = 0
        self.long_click_action_name = None
        self.long_click_cancel_message = self.app.app_state
        self.on_long_click = None
        self.on_short_click = None
        self.long_click_duration = 3
        self.long_cick_wait_started = False
        self.waiting_for_button_up = False
        logging.debug("Button {} inititated".format(name))

    def __check_long_click(self):
        if not self.on_long_click:
            return False
        if not self.button_down_since:
            return False
        if not self.is_down:
            self.long_cick_wait_started = False
            self.app.detail(self.long_click_action_name + " request cancelled")
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
                self.long_cick_wait_started = True
                pt = self.long_click_duration - t
                if self.long_click_action_name and self.last_print_time != pt:
                    self.app.print(
                        self.long_click_action_name + "? " + str(pt))
                    self.last_print_time = pt
            return False
        self.on_long_click()
        return True

    def __check_short_click(self):
        if not self.on_short_click:
            return False
        if self.long_cick_wait_started:
            return False
        if self.button_down_since and not self.is_down:
            self.on_short_click()
            return True
        return False

    def loop(self):
        if self.is_down and self.waiting_for_button_up:
            return False
        self.waiting_for_button_up = False
        if not self.button_down_since and self.is_down:
            self.button_down_since = time.time()
        if self.__check_short_click():
            return True
        return self.__check_long_click()


class SinglePinButton(HatButton):
    def __init__(self, name, app, pin):
        super().__init__(name, app)
        self.pin = pin
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.waiting_for_button_up = not GPIO.input(self.pin)

    def loop(self):
        self.is_down = not GPIO.input(self.pin)
        return super().loop()


class DoublePinButton(HatButton):
    def __init__(self, name, app, pin1, pin2):
        super().__init__(name, app)
        self.pin1 = pin1
        self.pin2 = pin2
        GPIO.setup(pin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def loop(self):
        self.is_down = not (GPIO.input(self.pin1) or GPIO.input(self.pin2))
        return super().loop()
