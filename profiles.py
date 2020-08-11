import json
import sys

from application import COMMAND_LINE_PARAM_CONFIG_FILE


class Profiles:
    def __init__(self):
        self.data = []
        self.prescript = []
        self.postscript = []
        file_name = 'profiles.json'
        if len(sys.argv) >= COMMAND_LINE_PARAM_CONFIG_FILE + 1:
            file_name = sys.argv[COMMAND_LINE_PARAM_CONFIG_FILE]
        print("Reading profiles from {}".format(file_name))
        with open(file_name) as f:
            self.data = json.load(f)

    def profile_by_jumper(self, jumper):
        for x in self.data:
            if not "jumper" in x:
                continue
            if x["jumper"] == jumper:
                return x
        raise Exception("No profile defined for jumper {}".format(jumper))

    def profile_by_id(self, profile_id):
        for x in self.data:
            if x["id"] == profile_id:
                return x
        raise Exception("Profile %s  not found" % profile_id)
