import json
import sys
import urllib.request, json 
from application import  Application, COMMAND_LINE_PARAM_CONFIG_FILE

profile_data = None

def init_profile_data(app):
    global profile_data
    file_name = "profiles.json"
    if len(sys.argv) >= COMMAND_LINE_PARAM_CONFIG_FILE + 1:
        p = sys.argv[COMMAND_LINE_PARAM_CONFIG_FILE]
        if (p.startswith("http")):
            app.profiles_url = p
        else:
            file_name = p
    if (app.profiles_url):
        app.detail("Loding profiles from " + app.profiles_url)
        with urllib.request.urlopen(app.profiles_url) as url:
            profile_data = json.loads(url.read().decode())
        return
    app.detail("Loading local profiles")
    if len(sys.argv) >= COMMAND_LINE_PARAM_CONFIG_FILE + 1:
        file_name = sys.argv[COMMAND_LINE_PARAM_CONFIG_FILE]
    with open(file_name) as f:
        profile_data = json.load(f)
    print(profile_data)

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
