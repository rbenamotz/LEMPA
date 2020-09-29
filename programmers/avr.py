import logging
import subprocess
from . import Programmer
from application import Application


class avr(Programmer):
    def __init__(self, app, profile):
        super().__init__(app)
        self.app = app
        self.profile = profile
        self.programming_speed = 125000
        if "speed" in self.profile:
            self.programming_speed = self.profile["speed"]

    def __run_avrdude__(self, params):
        command = "/usr/bin/sudo avrdude {}".format(params)
        process = subprocess.Popen(command.split(), stderr=subprocess.PIPE)
        while True:
            output = process.stderr.readline()
            if len(output) == 0 and process.poll() is not None:
                break
            if output:
                self.app.detail(output.strip().decode('utf-8'))
        rc = process.poll()
        return (rc == 0)

    def __burn_fuses__(self):
        self.app.print("Burning fuses")
        f = self.profile["fuses"]
        command: str = '-p {} -C ./avrdude_profile.conf -c linuxspi -P /dev/spidev0.0 -b {} ' \
                       '-D -e -u -U lfuse:w:{}:m -U hfuse:w:{}:m'.format(
                           self.profile["device"], self.programming_speed, f["lfuse"], f["hfuse"])
        if "efuse" in f:
            command = '{} -U efuse:w:{}:m'.format(command, f["efuse"])
        if "lock" in f:
            command = '{} -U lock:w:{}:m'.format(command, f["lock"])
        return self.__run_avrdude__(command)

    def __write_flash__(self):
        self.app.print("Writing flash")
        b = self.profile["bins"][0]
        command: str = "-p %s -C ./avrdude_profile.conf -c linuxspi -P /dev/spidev0.0 -b %s -u -U flash:w:bins/%s.hex:i -u  -e " % (
            self.profile["device"], self.programming_speed, b["name"])
        logging.debug(command)
        return self.__run_avrdude__(command)

    def program(self):
        b = self.__burn_fuses__()
        if not b:
            return False
        return self.__write_flash__()