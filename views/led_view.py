import RPi.GPIO as GPIO
import threading
import time


import application
from views import View
from hardware import PIN_BLUE, PIN_GREEN, PIN_RED, PIN_BLUE2

ALL_PINS = [PIN_BLUE, PIN_GREEN, PIN_RED, PIN_BLUE2]


class LedsView(View):
    def __init__(self, app):
        super().__init__(app)
        for p in ALL_PINS:
            GPIO.setup(p, GPIO.OUT)
        self.blink_state_fast = False
        self.blink_state_slow = False
        blinker = threading.Thread(target=self.blink, daemon=True)
        blinker.start()

    def blink(self):
        cnt = 0
        while True:
            self.refresh()
            time.sleep(0.1)
            self.blink_state_fast = not self.blink_state_fast
            cnt = cnt + 1
            if cnt ==5:
                self.blink_state_slow = not self.blink_state_slow
                cnt = 0

    def __update_blue(self):
        if self.app.app_state == application.Application.APP_STATE_PROGRAMMING:
            self.blink_gpio = PIN_BLUE
        b = (self.app.app_state == application.Application.APP_STATE_INIT)
        b = b or (self.app.app_state == application.Application.APP_STATE_WAITING_FOR_BUTTON)
        b = b or (self.blink_state_fast and self.app.app_state == application.Application.APP_STATE_PROGRAMMING)
        b = b or self.app.app_state == application.Application.APP_STATE_ERASE
        GPIO.output(PIN_BLUE, b)

    def __update_green(self):
        b = (self.app.app_state == application.Application.APP_STATE_INIT)
        b = b or (self.app.app_state == application.Application.APP_STATE_SUCCESS)
        b = b or (self.blink_gpio == PIN_GREEN and self.blink_state_fast)
        GPIO.output(PIN_GREEN, b)

    def __update_red(self):
        b = (self.app.app_state == application.Application.APP_STATE_INIT)
        b = b or (self.app.app_state == application.Application.APP_STATE_FAIL)
        b = b or (self.blink_state_fast and self.app.app_state == application.Application.APP_STATE_ERASE)
        b = b or (self.blink_state_slow and self.app.app_state == application.Application.APP_STATE_EXCEPTION)
        GPIO.output(PIN_RED, b)

    def __update_blue_2(self):
        b = (self.app.app_state == application.Application.APP_STATE_INIT)
        b = b or (self.app.app_state == application.Application.APP_STATE_FIRMWARE_DOWNLOAD)
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
