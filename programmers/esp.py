import esptool
from . import Programmer
from hardware import SERIAL_PORT
import RPi.GPIO as GPIO
import time
from hardware import PIN_ESP_RESET


class esp(Programmer):
    def __init__(self, app, profile):
        super().__init__(app, profile)

    def __reset_device__(self):
        self.app.detail("Resetting device")
        GPIO.output(PIN_ESP_RESET, False)
        time.sleep(0.1)
        GPIO.output(PIN_ESP_RESET, True)
        time.sleep(0.1)
        GPIO.output(PIN_ESP_RESET, False)

    def program(self):
        self.__reset_device__()
        command = [
            "--port",
            SERIAL_PORT,
            "--baud",
            str(self.programming_speed),
            "write_flash",
        ]
        for b in self.profile["bins"]:
            command.append(b["addr"])
            command.append("bins/%s.hex" % (b["name"]))
        try:
            esptool.main(command)
        except Exception as e:
            self.app.error(e)
            return False
        self.__reset_device__()
        return True
