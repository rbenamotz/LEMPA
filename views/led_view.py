import RPi.GPIO as GPIO
import threading
import time


import application
from views import View

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
        self.blink_state = False
        blinker = threading.Thread(target=self.blink, daemon=True)
        blinker.start()

    def blink(self):
        while True:
            self.refresh()
            time.sleep(0.1)
            self.blink_state = not self.blink_state

    def __update_blue(self):
        if self.app.app_state == application.Application.APP_STATE_PROGRAMMING:
            self.blink_gpio = PIN_BLUE
        b = False
        b = b or (self.app.app_state == application.Application.APP_STATE_WAITING_FOR_BUTTON)
        b = b or self.app.blue_led_on
        b = b or (self.blink_state and self.app.app_state == application.Application.APP_STATE_PROGRAMMING)
        b = b or (not self.blink_state and self.app.app_state == application.Application.APP_STATE_ERASE)
        GPIO.output(PIN_BLUE, b)

    def __update_green(self):
        b = False
        b = b or (self.app.app_state == application.Application.APP_STATE_SUCCESS)
        b = b or self.app.green_led_on
        b = b or (self.blink_gpio == PIN_GREEN and self.blink_state)
        GPIO.output(PIN_GREEN, b)

    def __update_red(self):
        b = False
        b = b or (self.app.app_state == application.Application.APP_STATE_FAIL)
        b = b or self.app.red_led_on
        b = b or (self.blink_state and self.app.app_state == application.Application.APP_STATE_ERASE)
        GPIO.output(PIN_RED, b)

    def __update_blue_2(self):
        b = (self.app.app_state == application.Application.APP_STATE_FIRMWARE_DOWNLOAD)
        GPIO.output(PIN_BLUE2, b)

    def refresh(self):
        self.blink_gpio = -1
        self.__update_blue()
        self.__update_green()
        self.__update_red()
        self.__update_blue_2()

    def cleanup(self):
        for p in ALL_PINS:
            GPIO.output(p, False)
