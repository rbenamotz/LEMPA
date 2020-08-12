import os
import urllib.request
from pathlib import Path

import requests

from application import Application
from .state import State


class FirmwareDownload(State):
    def __init__(self, app):
        super().__init__(app)
        self.profile_index = 0
        if not os.path.exists('./bins'):
            os.makedirs('./bins')

    def __download_cloud__(self, b):
        bin_file = "./bins/%s.hex" % (b["name"])
        self.app.print("Downloading {}".format(b["name"]))
        if "url" in b:
            download_url = b["url"]
        elif "info_url" in b:
            info_url = b["info_url"]
            r = requests.get(info_url)
            o = r.json()
            download_url = o["url"]
        else:
            raise Exception("Method is cloud but URL data was given")
        urllib.request.urlretrieve(download_url, bin_file)
        p = Path(bin_file).stat()
        self.app.print("{} bytes downloaded\n-----".format(p.st_size))

    def __validate_local_bin(self, b):
        bin_file = "./bins/%s.hex" % (b["name"])
        if not os.path.exists(bin_file):
            raise Exception("{} does not exist".format(bin_file))
        self.app.print("{} exists on disk".format(b["name"]))

    def do_step(self):
        if not self.app.dl_led_on:
            self.app.dl_led_on = True
            return False
        profile = self.app.profiles[self.profile_index]
        # TODO: Seriously??? Else if? Might as well program in BASIC
        for b in profile["bins"]:
            m = b["method"]
            if m == "cloud":
                self.__download_cloud__(b)
            elif m == "local":
                self.__validate_local_bin(b)
            else:
                raise Exception("Unknown bin method {}".format(m))
        self.profile_index = self.profile_index + 1

        if len(self.app.profiles) > self.profile_index:
            return False
        return True

    def on_event(self, event):
        self.app.dl_led_on = False
        return Application.APP_STATE_WAITING_FOR_BUTTON
