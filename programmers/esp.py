import esptool
from . import Programmer
from hardware import SERIAL_PORT
import RPi.GPIO as GPIO
import time
from hardware import PIN_ESP_RESET


class esp(Programmer):
    def __init__(self, app, profile):
        super().__init__(app, profile)

    def __reset_device(self):
        self.app.detail("Resetting device")
        GPIO.output(PIN_ESP_RESET, True)
        time.sleep(0.1)
        GPIO.output(PIN_ESP_RESET, False)
        time.sleep(0.1)
        GPIO.output(PIN_ESP_RESET, True)

    def program(self):
        command = [
            "--port",
            SERIAL_PORT,
            "--baud",
            str(self.comm_speed),
            "write_flash",
        ]
        for b in self.profile["bins"]:
            command.append(b["addr"])
            command.append("bins/%s.hex" % (b["name"]))
        try:
            self.__reset_device()
            self.app.detail(command)
            esptool.main(command)
            self.__reset_device()
        except Exception as e:
            self.app.error(e)
            return False
        return True
