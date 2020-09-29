from views import View
import application
import logging
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import time
from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class DisplayView(View):
    fonts_folder = Path(__file__).parents[0] / "fonts/"

    def __get_icon__(self):
        state = self.app.app_state
        if (state == application.Application.APP_STATE_WAITING_FOR_BUTTON):
            return '\uf0a5'
        if (state == application.Application.APP_STATE_PROGRAMMING):
            return '\uf0c7'
        if (state == application.Application.APP_STATE_ERASE):
            return '\uf2ed'
        if (state == application.Application.APP_STATE_SUCCESS):
            return '\uf118'
        if (state == application.Application.APP_STATE_FAIL):
            return '\uf119'
        if (state == application.Application.APP_STATE_FIRMWARE_DOWNLOAD):
            return '\uf358'
        return None

    def __init__(self, app):
        super().__init__(app)
        self.disp_header = ""
        self.disp_body = ""
        self.disp_error = None
        self.is_display_connected = False
        try:
            self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
            self.disp.begin()
            self.disp.command(Adafruit_SSD1306.SSD1306_DEACTIVATE_SCROLL)
            self.is_display_connected = True
        except OSError as e:
            logging.error(e)
            logging.warning("Could not initialize display. Well... LEDs should suffice")
            return
        self.disp.clear()
        self.disp.display()
        width = self.disp.width
        height = self.disp.height
        self.image = Image.new('1', (width, height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()
        self.fontHeader = ImageFont.truetype(str(self.fonts_folder) + "/Arimo.ttf", 10)
        self.fontBody = ImageFont.truetype(str(self.fonts_folder) + "/Arimo.ttf", 12)
        self.fontIcon = ImageFont.truetype(str(self.fonts_folder) + "/FontAwesomeRegular.ttf", 10)

    def __refresh(self):
        if not self.is_display_connected:
            return
        self.draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)
        y = 0
        self.draw.text((0,y), self.disp_header, font = self.fontHeader, fill=1)
        icon = self.__get_icon__()
        if icon:
            self.draw.text((118,y), icon, font = self.fontIcon, fill=1)
        y = y + 12
        self.draw.line([(0,y),(self.disp.width,y)],fill=1)
        y = y + 3
        if self.disp_error:
            self.draw.text((0,y), self.disp_error, font = self.fontBody, fill=1)
        else:
            self.draw.text((0, y),self.disp_body, font=self.fontBody, fill=1)
        self.disp.image(self.image)
        self.disp.display()

    def cleanup(self):
        if not self.is_display_connected:
            return
        self.disp.clear()
        self.disp.display()

    def print(self, txt):
        self.disp_body = txt
        self.__refresh()

    def error(self, e):
        self.disp_header = "[error]"
        self.disp_body = str(e)
        self.__refresh()

    def header(self):
        self.disp_header = self.app.profile_name
        self.disp_body = self.app.app_state
        self.__refresh()
