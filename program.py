#!/usr/bin/env python3

import logging
import time
import RPi.GPIO as GPIO
import traceback
import sys


from application import Application
from states.state_factory import *

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', filename='LEMPA.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())
logging.info("Programmer is running")


def load_state(code):
    global app
    app.app_state = code
    output = state_by_code(code, app)
    return output


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
        logging.info("LEMPA stopped due to Keyboard Interrupt")
        break
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        state = load_state(Application.APP_STATE_EXCEPTION)
        app.error(e)
GPIO.cleanup()
