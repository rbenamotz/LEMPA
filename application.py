from views.led_view import LedsView
from views.terminal_view import TerminalView

COMMAND_LINE_PARAM_PROFILE_ID = 1
COMMAND_LINE_PARAM_CONFIG_FILE = 2


class Application:
    APP_STATE_PROFILE_SENSE = "Profile Sensing"
    APP_STATE_INIT = "Initializing"
    APP_STATE_FIRMWARE_DOWNLOAD = "Firmware Download"
    APP_STATE_WAITING_FOR_BUTTON = "Push button to start"
    APP_STATE_CHECKING_UPDATE = "Cloud"
    APP_STATE_PROGRAMMING = "Programming"
    APP_STATE_SUCCESS = "Success"
    APP_STATE_FAIL = "Fail"

    def update_views(self):
        for v in self.views:
            v.update()

    def __init__(self):
        self.blue_led_on = False
        self.green_led_on = False
        self.red_led_on = False
        self.dl_led_on = False
        self.firmware_version = 0
        self.__app_state = self.APP_STATE_PROFILE_SENSE
        self.profiles = []
        self.plugins = []
        self.views = [TerminalView(self), LedsView(self)]

    def refresh_views(self):
        for v in self.views:
            v.refresh()

    def clean_views(self):
        for v in self.views:
            v.cleanup()

    def print(self, txt):
        for v in self.views:
            v.print(txt)

    def error(self, e):
        for v in self.views:
            v.error(e)

    @property
    def app_state(self):
        return self.__app_state

    @app_state.setter
    def app_state(self, app_state):
        self.__app_state = app_state
        for v in self.views:
            v.header()
