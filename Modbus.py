# coding=utf-8

from time import sleep
import serial
from struct import unpack
from byte_util import str2int_list, int_list2hex_str

class Modbus:
    def __init__(self,PORT="COM20",\
                 BAUDR="19200",\
                 PAR=serial.PARITY_NONE,\
                 BSTOP=serial.STOPBITS_ONE,\
                 BSIZE=serial.EIGHTBITS,\
                 TIMEOUT = None,\
                 INTERCHARTIMEOUT = None
                 ):
        self.ser = serial.Serial(
        port=PORT,\
        baudrate=BAUDR,\
        parity=PAR,\
        stopbits=BSTOP,\
        bytesize=BSIZE,\
        timeout=TIMEOUT,\
        interCharTimeout=INTERCHARTIMEOUT)

    def __del__(self):
        if self.ser:
            self.ser.close()

    def close(self):
        if self.ser:
            self.ser.close()

    def read(self,length):
        read_raw = self.ser.read(length)
        return list(unpack('B'*len(read_raw), str(bytearray(read_raw))))

    def write(self,data,time=1,delay=0.06):
        for i in range(time):
            self.ser.write(data)
            sleep(delay)
    def flush(self):
        self.ser.flushInput()

# b = Modbus(PORT="COM2",BAUDR="9600",TIMEOUT=0.05)
# b.ser.flush()
# b.write(str2int_list("FE FF FF FF 55 55 FE 9A"))