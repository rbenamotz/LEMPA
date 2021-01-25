from hardware import SERIAL_PORT, DEFAULT_SERIAL_SPEED
import serial
import logging
import time
import application

from serial import SerialException

ser = None
serial_speed = DEFAULT_SERIAL_SPEED




def init_serial():
    global ser
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=serial_speed,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1,
        writeTimeout=0,
    )
    logging.info(
        "Serial connection initiated to {} with speed {:,d}bps".format(
            SERIAL_PORT, serial_speed
        )
    )

def validate_serial():
    if ser is None:
        raise SerialException(
            "Serial not available. Try to enable Serial with raspi-config")


def export_text(txt):
    global ser
    validate_serial()
    ser.write(txt.encode())

def export_config(conf):
    validate_serial()
    packet = bytearray()
    for f in conf:
        i = int(f["value"])
        packet.append(i)
    ser.write(packet)



def close_serial():
    global ser
    if (ser):
        ser.close()
        ser = None


class SerialConnectionThread():
    def __init__(self, serial_in_callback, status_callback):
        self.should_connect = False
        self.status_callback = status_callback
        self.serial_in_callback = serial_in_callback
    def reconnect(self):
        global ser
        if ser:
            return
        if (self.status_callback):
            self.status_callback()
        init_serial()
        while ser is None and self.should_connect:
            time.sleep(0.2)
        if (self.status_callback):
            self.status_callback()

    def read_line(self):
        global ser
        l = ser.readline()
        if (len(l) ==0):
            time.sleep(0.1)
            return
        s = l.decode("utf-8", errors="replace")
        self.serial_in_callback(s)

    def state_changed(self, new_state):
        self.should_connect = (new_state == application.Application.APP_STATE_WAITING_FOR_BUTTON)
        if not self.should_connect:
            close_serial()
            print ("serial closed")

    def run(self):
        global ser
        while True:
            try:
                while (not self.should_connect):
                    time.sleep(0.1)
                    continue
                self.reconnect()
                if (self.should_connect):
                    self.read_line()
                # time.sleep(0.1)
            except SerialException:
                ser = None
            except Exception as e:
                logging.error(e)
                #raise
        if ser:
            logging.info("Closing Serial")
            ser.close()
            ser = None
