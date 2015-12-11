from bitstring import BitArray

def List2Ascii(lst):
    asc = ""
    if isinstance(lst, list):
        for i in lst:
            asc += chr(i)
    return asc


def List2Str(lst):
    return Ascii2Str(List2Ascii(lst))

def List2Int(relay_status):
    status = 0
    for i in range(len(relay_status)):
        if(relay_status[i] == 1):
            status += 2**i
    return status
    pass

def Ascii2Str(asc):
    return asc.encode('hex')


def Ascii2Hexlist(asc):
    return Ascii2Str(asc).decode('hex')


def Str2Ascii(str):
    return str.decode('hex')


def crc16_le(byte_list):
    b = 0xA001
    a = 0xFFFF
    for byte in byte_list:
        a = a ^ byte
        for i in xrange(8):
            last = a % 2
            a = a >> 1
            if last == 1: a = a ^ b
    aa = '0' * (6 - len(hex(a))) + hex(a)[2:]
    ll, hh = int(aa[:2], 16), int(aa[2:], 16)
    return [hh, ll]


def ListAddCrc(lst):
    crc = []
    if isinstance(lst, list):
        crc = crc16_le(lst)
    for i in crc:
        lst.append(i)
    return lst


def ListCheckCrc(lst):
    ret = True
    lst_data = lst[:-2]
    list_crc = lst[-2:]
    check_crc = crc16_le(lst_data)

    if list_crc != check_crc:
        ret = False
    return ret


def Int2Listbin(data):
    return list(BitArray(hex(data)).bin.zfill(8))

