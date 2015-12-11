# coding=utf-8
from time import sleep
import serial
from struct import unpack
from Modbus import ModbusWindows
from TException import TException
from Utils import List2Str
from Utils import ListAddCrc
from Utils import ListCheckCrc
from Utils import Int2Listbin
from Utils import List2Ascii
from Utils import List2Int
import ConfigParser

cf = ConfigParser.ConfigParser()
cf.read("./conf.ini")

# 波特率、数据位、校验位、停止位转义列表
BAUD_LIST = ["2400", "4800", "9600", "19200", "38400", "57600", "115200"]
BYTE_LIST = [8]
PARITY_LIST = ['N', 'E', 'O']
STOP_LIST = [1, 2]


class ICS(ModbusWindows):

    def __init__(self, port, addr):
        self.addr = addr  # 485地址
        self.switch_mode = 0  # 干接点模式 1：长触模式，0：短触模式
        self.switch_status = [0, 0, 0]  # 干接点状态
        self.relay_status = [0, 0, 0]  # 继电器状态
        self.id = []
        self.baudrate = int(cf.get("serial", "baudrate"))
        self.bytesize = int(cf.get("serial", "bytesize"))
        self.parity = int(cf.get("serial", "parity"))
        self.stop = int(cf.get("serial", "stop"))

        ModbusWindows.__init__(self,
                               PORT=port,
                               BAUDR=BAUD_LIST[self.baudrate - 1],
                               BSIZE=BYTE_LIST[self.bytesize - 1],
                               PAR=PARITY_LIST[self.parity - 1],
                               BSTOP=STOP_LIST[self.stop - 1],
                               TIMEOUT=1000)

    def write(self, cmd):
        ModbusWindows.write(self, List2Ascii(cmd))

    def read(self, length):
        read_raw = ModbusWindows.read(self, length)
        return list(unpack('B' * len(read_raw), str(bytearray(read_raw))))

    # 初始化
    def Init(self):
        self.id = self.GetId()
        self.GetStatus()

    # 获取ID
    # return 返回ID的数组
    def GetId(self):
        cmd = [self.addr, 3, 0x80, 0, 0, 6]
        ListAddCrc(cmd)
        self.write(cmd)
        sleep(0.05)
        ret = self.read(17)
        if not ListCheckCrc(ret):
            raise TException('Id Checksum Error! ID:%s' %
                             List2Str(ret))
        return ret[3:15]
        pass

    # 获取网络模式、点触模式、继电器状态、干接点状态
    def GetStatus(self):
        cmd = [self.addr, 2, 0, 0, 0, 6]
        cmd = ListAddCrc(cmd)
        self.write(cmd)
        sleep(0.05)
        ret = self.read(6)
        if not ListCheckCrc(ret):
            raise TException('GetStatus Checksum Error! ID:%s' %
                             List2Str(ret))
        else:
            status = Int2Listbin(ret[3])
            status.reverse()
            self.switch_status = status[0:3]
            self.relay_status = status[3:6]
            self.switch_mode = status[6]
            self.network_mode = status[7]

    # 获取干接点状态
    def GetSwitchStatus(self):
        self.GetStatus()
        return self.switch_status
        pass

    # 获取点触模式，长触/短触
    def GetSwitchMode(self):
        self.GetStatus()
        return self.switch_mode
        pass

    # [Boardcast]修改串口配置
    # 需要重启才能生效
    # 参数分别是波特率，数据位，校验位，停止位
    def SetSerialConfig(self, baudrate="9600", data_number=8, check_number='N', stop_number=1):
        temp_baudrate = BAUD_LIST.index(baudrate) + 1
        temp_bytesize = BYTE_LIST.index(data_number) + 1
        temp_parity = PARITY_LIST.index(check_number) + 1
        temp_stop = STOP_LIST.index(stop_number) + 1
        print temp_baudrate
        print temp_bytesize
        print temp_parity
        print temp_stop

        if temp_baudrate != self.baudrate or \
                        temp_bytesize != self.bytesize or \
                        temp_parity != self.parity or \
                        temp_stop != self.stop:
            # 设置0xA000寄存器
            _A000_value = temp_baudrate << 4
            _A000_value += temp_bytesize
            print "A000 register value is: 0x%x" % _A000_value
            # 设置0xA001寄存器
            _A001_value = temp_parity << 4
            _A001_value += temp_stop
            print "A001 register value is: 0x%x" % _A001_value
            cmd = [0, 6, 0xA0, 0, _A000_value, _A001_value]
            ListAddCrc(cmd)
            print List2Str(cmd)
            self.write(cmd)

            cf.set("serial", "baudrate", temp_baudrate)
            cf.set("serial", "bytesize", temp_bytesize)
            cf.set("serial", "parity", temp_parity)
            cf.set("serial", "stop", temp_stop)

            cf.write(open("./conf.ini","w"))
        else:
            print "same config."
        pass

    # [Single|Boardcast]修改点触模式，长触/短触
    # 需要重启才能生效
    def SetSwitchMode(self, is_broadcast=False, is_hold=True):
        send_addr = 0  # 0是组播，非组播是地址值
        hold_mode = 0  # 0是短触，1是长触

        if not is_broadcast:
            send_addr = self.addr

        if is_hold:
            hold_mode = 1

        cmd = [send_addr, 6, 0xA0, 4, 0, hold_mode]
        ListAddCrc(cmd)
        print List2Str(cmd)
        self.write(cmd)

        if not is_broadcast:
            ret = self.read(8)
            print List2Str(ret)
        pass


class ICS10(ICS):

    def __init__(self, port, addr):
        ICS.__init__(self, port, addr)

    # TODO
    # 获取上报模式，主动/被动
    def GetAckMode(self):
        pass

    # TODO
    # [Boardcast]修改上报模式，主动/被动
    def SetAckMode(self):
        pass

    pass


class ICS20(ICS):

    def __init__(self, port, addr):
        ICS.__init__(self, port, addr)
        self.network_mode = 0  # 网络模式 0：本地模式，1：非本地模式
        self.relay_status = [0, 0, 0]  # 继电器状态

    # 获取继电器状态
    def GetRelayStatus(self):
        self.GetStatus()
        return self.relay_status
        pass

    # 获取通讯模式，远程/本地
    def GetNetworkMode(self):
        self.GetStatus()
        return self.network_mode
        pass

    # 控制继电器
    def SetRelay(self, relay_status):
        status = List2Int(relay_status)
        cmd = [self.addr, 0x0F, 0x00, 0x03, 0x00, 0x03, 0x01, status]
        ListAddCrc(cmd)
        self.write(cmd)
        sleep(0.05)
        ret = self.read(8)
        if not ListCheckCrc(ret):
            raise TException('SetRelay Checksum Error! Response:%s' %
                             List2Str(ret))
        ret_check = [self.addr, 0x0f, 0, 3, 0, 3]
        ListAddCrc(ret_check)
        if ret != ret_check:
            raise TException('SetRelay Response Error! Response:%s' %
                             List2Str(ret))
        pass

    # [Single|Boardcast]修改通讯模式，本地/远程
    def SetNetworkMode(self, is_broadcast=False, is_local=True):
        send_addr = 0  # 0是组播，非组播是地址值
        network_mode = 1  # 1是非本地模式，0是本地模式

        if not is_broadcast:
            send_addr = self.addr

        if is_local:
            network_mode = 0

        cmd = [send_addr, 6, 0xA0, 2, 0, network_mode]
        ListAddCrc(cmd)
        print List2Str(cmd)
        self.write(cmd)

        if not is_broadcast:
            ret = self.read(8)
            print List2Str(ret)
        pass

    pass


ics = ICS20("COM6", 1)
try:
    ics.Init()
    print "id:"
    print List2Str(ics.id)
    # print "network mode:"
    # print ics.network_mode
    # print "switch mode:"
    # print ics.switch_mode
    # print "relay status:"
    # print ics.relay_status
    # print "switch status:"
    # print ics.switch_status

    # print "init, relay status:"
    # print ics.GetRelayStatus()
    # ics.SetRelay([1, 0, 0])
    # sleep(0.3)
    # ics.SetRelay([1, 1, 0])
    # sleep(0.3)
    # ics.SetRelay([1, 1, 1])
    # print "after set on, relay status:"
    # print ics.GetRelayStatus()

    # sleep(2)

    # ics.SetRelay([0, 1, 1])
    # sleep(0.3)
    # ics.SetRelay([0, 0, 1])
    # sleep(0.3)
    # ics.SetRelay([0, 0, 0])
    # print "after set off, relay status:"
    # print ics.GetRelayStatus()

    # ics.SetNetworkMode(False, True)
    # ics.SetSwitchMode(False, True)
    # ics.SetSerialConfig(baudrate='19200')

    pass
except TException, e:
    print e
    pass
finally:
    ics.close()
pass
