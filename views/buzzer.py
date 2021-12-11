import RPi.GPIO as GPIO
import threading
import time
import application
from views import View
from hardware import PIN_BUZZER
from rtttl import parse_rtttl

SONG_TWO_SHORT = "two short:d=4,o=5,b=100:16e6,16e6"
SONG_ONE_SHORT = "one short:d=4,o=5,b=100:16e6"
SONG_ERROR = "error:d=4,o=5,b=100:16a6,16a6,16a6,16a6,16a6,16a6,16a6"
SONG_SUCCESS = "success:d=4,o=5,b=100:16a4,16b4,16c4,16d4,16e4,16f4,16g4,16e4,16d4,16c4,16b4,16a4"
SONG_MCGYVER = "McGyver:d=4,o=4,b=160:8c5,8c5,8c5,8c5,2b,8f#,a,2g,8c5,c5,b,8a,8b,8a,g,e5,2a,b.,8p,8c5,8b,8a,c5,8b,8a,d5,8c5,8b,d5,8c5,8b,e5,8d5,8e5,f#5,b,1g5,8p,8g5,8e5,8c5,8f#5,8d5,8b,8e5,8c5,8a,8d5,8b,8g,c5,b,8c5,8b,8a,8g,a#,a,8g"


class BuzzerView(View):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pending_song = None
        GPIO.setup(PIN_BUZZER, GPIO.OUT)
        t = threading.Thread(target=self.orchestra, daemon=True)
        t.start()

    def play_next_song(self, buzzer):
        if not self.pending_song:
            return
        if not self.app.buzzer_enabled:
            self.pending_song = None
            return
        song = parse_rtttl(self.pending_song)
        self.pending_song = None
        for note in song["notes"]:
            if (self.pending_song):
                buzzer.stop()
                break
            f = note["frequency"]
            time.sleep(note["duration"] / 2000 * 0.5)
            if (f > 0):
                buzzer.start(50)
                buzzer.ChangeFrequency(f)
            time.sleep(note["duration"] / 2000 * 0.5)
            buzzer.stop()
        time.sleep(0.5)

    def orchestra(self):
        buzzer = GPIO.PWM(PIN_BUZZER, 1000)
        try:
            while True:
                self.play_next_song(buzzer)
                time.sleep(0.1)
        except KeyboardInterrupt:
            return

    def print(self, txt):
        if (self.app.app_state ==application.Application.APP_STATE_SHUTDOWN):
            self.pending_song = SONG_ONE_SHORT
    def header(self):
        if (self.app.app_state == application.Application.APP_STATE_SUCCESS):
            self.pending_song = SONG_SUCCESS
            return
        if (self.app.app_state == application.Application.APP_STATE_FAIL):
            self.pending_song = SONG_ERROR
            return
        self.pending_song = SONG_ONE_SHORT
