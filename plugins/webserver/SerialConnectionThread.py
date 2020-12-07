from hardware import SERIAL_PORT, DEFAULT_SERIAL_SPEED
import serial
import logging
import time

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
        self.status_callback = status_callback
        self.serial_in_callback = serial_in_callback

    def run(self):
        global ser
        ba = bytearray()
        while True:
            try:
                if ser is None:
                    if (self.status_callback):
                        self.status_callback()
                    init_serial()
                    while ser is None:
                        time.sleep(0.2)
                    if (self.status_callback):
                        self.status_callback()
                b = ser.read()
                if b and b[0] > 0x00:
                    ba.append(ord(b))
                    if b == b"\n":
                        s = ba.decode("utf-8", errors="replace")
                        self.serial_in_callback(s)
                        ba = bytearray()
                else:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(e)
                # break
        if ser:
            print("!!!!!!!!!!!!Closing Serial!!!!!!!!!!!!!!!!!")
            ser.close()
            ser = None
