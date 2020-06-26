from struct import *
from binascii import hexlify

def ten_bit_signed(value):
    print("Got value: " + str(value))
    sign = '1' if value < 0 else '0'
    return sign + bin(abs(value))[2:].zfill(9)

def seven_bit_unsigned(value):
    return bin(abs(value & 0x3f))[2:].zfill(7)

for value in [ bytearray(b'\xf3\x00\x00\x9d\x03\x00\x00&l\x01\x02<\x00\xfb4\x9b'),
               bytearray(b'2\x01\x00\xfc\x1a\x00\x00(r\x01\x02<\x00\xfb4\x9b'),
               bytearray(b'\x06\x01\x00B\x05\x00\x00%]\x01\x02<\x00\xfb4\x9b') ]:
    le_data = unpack('<HBIBHHI', value)
    be_data = unpack('>HBIBHHI', value)
    data = {
      'temperature': le_data[0]/10,
      'light': le_data[2],
      'moisture': be_data[3],
      'fertility': le_data[4]
    }
    print("Data: " + str(data))
    # 0       1       2       3       4       5       6       7       8       9       10      11
    # 100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000
    # P---T---xxxxV---dt--------at--------hu-----st--------sm-----xuv-LU--------------IR--------------
    # P - Protocol
    # T - ProbeType
    # V - Version
    # dt - Device temp signed (10)
    # at - Air temp signed (10)
    # hu - Air humidity unsigned (7)
    # st - Soil temp signed (10)
    # sm - Soil moisture unsigned (7)
    # uv - Ultraviolet unsigned (3)
    # LU - Visible light (16)
    # IR - Infrared light (16)
    bytes_data = bytearray(b'\x12\x01')
    binary_string = '';
    binary_string += ten_bit_signed(int(data['temperature'] * 10))
    print("1: " + binary_string + " (" + str(len(binary_string)) + ")")
    binary_string += ten_bit_signed(int(data['temperature'] * 10))
    print("2: " + binary_string + " (" + str(len(binary_string)) + ")")
    binary_string += '0000000' # Air humidity
    binary_string += '0000000000' # Soil temp
    binary_string += seven_bit_unsigned(data['moisture'])
    print("3: " + binary_string + " (" + str(len(binary_string)) + ")")
    binary_string += '0000' 
    print("4: " + binary_string + " (" + str(len(binary_string)) + ")")
    print("Hex: " + hex(int(binary_string, 2))[2:].zfill(12))
    final_string = "1201" + hex(int(binary_string, 2))[2:].zfill(12) + hex(data['light'])[2:].zfill(4) + '0000'
    print("Final: " + final_string)
