import RPi.GPIO as GPIO

import application
from views.view import View

PIN_RED = 23
PIN_GREEN = 24
PIN_BLUE = 20
PIN_BLUE2 = 25

ALL_PINS = [PIN_BLUE, PIN_GREEN, PIN_RED, PIN_BLUE2]


class LedsView(View):
    def __init__(self, app):
        super().__init__(app)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for p in ALL_PINS:
            GPIO.setup(p, GPIO.OUT)

    def __update_blue(self):
        b = False
        b = b or (self.app.app_state ==
                  application.Application.APP_STATE_WAITING_FOR_BUTTON)
        b = b or self.app.blue_led_on
        GPIO.output(PIN_BLUE, b)

    def __update_green(self):
        b = False
        b = b or (self.app.app_state ==
                  application.Application.APP_STATE_SUCCESS)
        b = b or self.app.green_led_on
        GPIO.output(PIN_GREEN, b)

    def __update_red(self):
        b = False
        b = b or (self.app.app_state == application.Application.APP_STATE_FAIL)
        b = b or self.app.red_led_on
        GPIO.output(PIN_RED, b)

    def __update_blue_2(self):
        b = self.app.dl_led_on
        GPIO.output(PIN_BLUE2, b)

    def refresh(self):
        self.__update_blue()
        self.__update_green()
        self.__update_red()
        self.__update_blue_2()

    def cleanup(self):
        for p in ALL_PINS:
            GPIO.output(p, False)
