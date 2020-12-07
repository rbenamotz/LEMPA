from programmers.avr import avr
from programmers.esp import esp


def create_programmer(app, profile):
    code = profile["programmer"]
    if code == "linuxspi":
        return avr(app, profile)
    if code == "esptool":
        return esp(app, profile)
    raise KeyError("Unknown programmer of type {}".format(code))
