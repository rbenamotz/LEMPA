#!/usr/bin/env python3

import logging
import time
import RPi.GPIO as GPIO
import traceback, sys


from application import Application
from states.env_init_state import EnvInit
from states.fail_state import FailState
from states.firmware_downloader import FirmwareDownload
from states.program_state import ProgramState
from states.sense_profile_state import SensingProfileState
from states.success_state import SuccessState
from states.wait_for_button_state import WaitForButtonState
from states.fw_erase import FirmwareEraseState
from states.exception_state import ExceptionState

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', filename='LEMPA.log', level=logging.WARNING)
logging.info("Programmer is running")


def load_state(code):
    app.app_state = code
    if code == Application.APP_STATE_INIT:
        return EnvInit(app)
    if code == Application.APP_STATE_PROFILE_SENSE:
        return SensingProfileState(app)
    if code == Application.APP_STATE_FIRMWARE_DOWNLOAD:
        return FirmwareDownload(app)
    if code == Application.APP_STATE_WAITING_FOR_BUTTON:
        return WaitForButtonState(app)
    if code == Application.APP_STATE_PROGRAMMING:
        return ProgramState(app)
    if code == Application.APP_STATE_SUCCESS:
        return SuccessState(app)
    if code == Application.APP_STATE_FAIL:
        return FailState(app)
    if code == Application.APP_STATE_ERASE:
        return FirmwareEraseState(app)
    if code == Application.APP_STATE_EXCEPTION:
        return ExceptionState(app)
    raise Exception("Unknown state %s" % code)

def cycle():
    global state
    app.refresh_views()
    event = False
    while not event:
        event = state.do_step()
        app.refresh_views()
        time.sleep(0.01)
    state_code = state.on_event(event)
    state = load_state(state_code)


GPIO.setmode(GPIO.BCM)
app = Application()
state = load_state(Application.APP_STATE_INIT)

while True:
    try:
        cycle()
    except KeyboardInterrupt:
        app.clean_views()
        break
    except Exception as e:
        logging.error(e)
        # traceback.print_exc()
        state = load_state(Application.APP_STATE_EXCEPTION)
        app.error(e)
GPIO.cleanup() 
