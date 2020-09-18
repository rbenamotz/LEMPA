from views.view import View
import logging
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class DisplayView(View):
    def __init__(self, app):
        self.disp_header = ""
        self.disp_body = "LEMPA"
        self.disp_error = None
        self.is_display_connected = False
        try:
            self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
            self.disp.begin()
            self.is_display_connected = True
        except OSError:
            logging.warning("Could not initialize display. Well... LEDs should suffice")
            return
        self.disp.clear()
        self.disp.display()
        width = self.disp.width
        height = self.disp.height
        self.image = Image.new('1', (width, height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()
        return View.__init__(self, app)

    def __refresh(self):
        if not self.is_display_connected:
            return
        self.draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)
        y = 0
        if self.disp_error:
            self.draw.text((0,y), self.disp_error, font = self.font, fill=1)
        else:
            self.draw.text((0,y), self.app.profile_name, font = self.font, fill=1)
            y = y + 10
            self.draw.text((0, y), self.app.app_state,  font=self.font, fill=1)
            y = y + 10
            self.draw.text((0, y),self.disp_body, font=self.font, fill=1)
        img = self.image.transpose(Image.ROTATE_180)
        self.disp.image(img)
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
        self.disp_error = str(e)
        # self.disp_body = e
    #     print('\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    #     print(e)
    #     print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n')

    def header(self):
        self.disp_body = ""
        self.__refresh()
