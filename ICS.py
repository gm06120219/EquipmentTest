# coding=utf-8

import Modbus

class ICS10(Modbus):
    def __init__(self,port="COM20",\
                 addr=1):

        pass

    # 获取ID
    def GetId(self):
        pass

    # 获取干接点状态
    def GetSwitchStatus(self):
        pass

    # 获取点触模式，长触/短触
    def GetSwitchMode(self):
        pass

    # 获取上报模式，主动/被动
    def GetAckMode(self):
        pass

    # [Boardcast]修改串口配置
    def SetSerialConfig(self):
        pass

    # [Single|Boardcast]修改点触模式，长触/短触
    def SetSwitchMode(self):
        pass

    # [Boardcast]修改上报模式，主动/被动
    def SetAckMode(self):
        pass

    pass


class ICS20(Modbus):
    # 获取ID
    def GetId(self):
        pass

    # 获取干接点状态
    def GetSwitchStatus(self):
        pass

    # 获取点触模式，长触/短触
    def GetSwitchMode(self):
        pass

    # 获取继电器状态
    def GetRelayStatus(self):
        pass

    # 获取通讯模式，远程/本地
    def GetNetworkMode(self):
        pass

    # [Boardcast]修改串口配置
    def SetSerialConfig(self):
        pass

    # [Single|Boardcast]修改点触模式，长触/短触
    def SetSwitchMode(self):
        pass

    # [Single|Boardcast]修改通讯模式，本地/远程
    def SetNetworkMode(self):
        pass

    # 控制继电器
    def SetDetry(self):
        pass

    pass