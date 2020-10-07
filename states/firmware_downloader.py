import os
import urllib.request
from pathlib import Path

import requests

from application import Application
from states import State
from .binfetchers.binfetcher_factory import  create_fetcher


class FirmwareDownload(State):
    def __init__(self, app):
        super().__init__(app)
        self.profile_index = 0
        if not os.path.exists('./bins'):
            os.makedirs('./bins')

    def __download_cloud__(self, b):
        bin_file = "./bins/%s.hex" % (b["name"])
        self.app.print("DL {}".format(b["name"]))
        if "url" in b:
            download_url = b["url"]
        elif "info_url" in b:
            info_url = b["info_url"]
            r = requests.get(info_url)
            o = r.json()
            download_url = o["url"]
        else:
            raise Exception("Missing URL for bin")
        self.app.detail(bin_file)
        self.app.detail(download_url)
        urllib.request.urlretrieve(download_url, bin_file)
        p = Path(bin_file).stat()
        self.app.detail("{} bytes downloaded".format(p.st_size))

    def __validate_local_bin(self, b):
        bin_file = "./bins/%s.hex" % (b["name"])
        if not os.path.exists(bin_file):
            raise Exception("{} does not exist".format(bin_file))
        self.app.detail("{} exists on disk".format(b["name"]))

    def do_step(self):
        profile = self.app.profiles[self.profile_index]
        # TODO: Seriously??? Else if? Might as well program in BASIC
        for b in profile["bins"]:
            m = b["method"]
            f = create_fetcher(m,self.app)
            f.fetch(b)
            continue
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
        return Application.APP_STATE_WAITING_FOR_BUTTON
