import json
import sys

from application import COMMAND_LINE_PARAM_CONFIG_FILE

all_profiles = []
file_name = 'profiles.json'
if len(sys.argv) >= COMMAND_LINE_PARAM_CONFIG_FILE + 1:
    file_name = sys.argv[COMMAND_LINE_PARAM_CONFIG_FILE]
#print("Reading profiles from {}".format(file_name))
with open(file_name) as f:
    profile_data = json.load(f)


def profile_by_jumper(jumper):
    for x in profile_data:
        if "jumper" not in x:
            continue
        if x["jumper"] == jumper:
            return x
    raise Exception("No profile defined for jumper {}".format(jumper))


def profile_by_id(profile_id):
    for x in profile_data:
        if x["id"] == profile_id:
            return x
    raise Exception("Profile %s not found" % profile_id)
