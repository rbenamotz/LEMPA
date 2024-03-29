import logging
from views.led_view import LedsView
from views.terminal_view import TerminalView
from views.display_view import DisplayView
from views.buzzer import BuzzerView
from views import View
from logging import StreamHandler, LogRecord

COMMAND_LINE_PARAM_PROFILE_ID = 1
COMMAND_LINE_PARAM_CONFIG_FILE = 2


class PlugingsList(list):
    def __init__(self, app):
        self.app = app
        super().__init__()

    def append(self, x):
        if isinstance(x, View):
            self.app.views.append(x)
        return super().append(x)


class Application (StreamHandler):
    APP_STATE_PROFILE_SENSE = "Profile Sensing"
    APP_STATE_INIT = "Initializing"
    APP_STATE_FIRMWARE_DOWNLOAD = "Firmware Download"
    APP_STATE_WAITING_FOR_BUTTON = "Push button"
    APP_STATE_CHECKING_UPDATE = "Cloud"
    APP_STATE_PROGRAMMING = "Programming"
    APP_STATE_SUCCESS = "Success"
    APP_STATE_FAIL = "Fail"
    APP_STATE_ERASE = "Erasing"
    APP_STATE_EXCEPTION = "Exception"
    APP_STATE_SHUTDOWN = "Shut down"

    should_exit = False

    def __init__(self):
        StreamHandler.__init__(self)
        self.my_name = "LEMPA"
        self.__profile_name__ = ""
        self.serial_port = None
        self.firmware_version = 0
        self.__app_state = self.APP_STATE_PROFILE_SENSE
        self.profiles = []
        self.skip_detect = False
        self.plugins = PlugingsList(self)
        self.views = [TerminalView(self), LedsView(
            self), DisplayView(self), BuzzerView(self)]
        self.profiles_url = None
        self.buzzer_enabled = True
        self.profile_info = {}
        self.move_to_state = None

    # def emit(self, record: LogRecord) -> None:
    #     msg = self.format(record)
    #     self.detail(msg)

    def update_views(self):
        for v in self.views:
            v.update()

    def refresh_views(self):
        for v in self.views:
            v.refresh()

    def clean_views(self):
        for v in self.views:
            v.cleanup()

    def print(self, txt):
        for v in self.views:
            v.print(txt)

    def detail(self, txt):
        for v in self.views:
            v.detail(txt)

    def error(self, e):
        for v in self.views:
            v.error(e)

    @property
    def app_state(self):
        return self.__app_state

    @property
    def profile_name(self):
        return self.__profile_name__

    @property
    def is_auto_detect(self):
        if "autodetect" not in self.profile_info:
            return False
        return self.profile_info["autodetect"]

    @profile_name.setter
    def profile_name(self, x):
        self.__profile_name__ = x
        for v in self.views:
            v.set_profile_name(x)

    @app_state.setter
    def app_state(self, app_state):
        self.__app_state = app_state
        for v in self.views:
            v.header()
