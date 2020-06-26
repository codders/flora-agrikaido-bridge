from struct import unpack

for value in [ bytearray(b'\xf3\x00\x00\x9d\x03\x00\x00&l\x01\x02<\x00\xfb4\x9b'),
               bytearray(b'2\x01\x00\xfc\x1a\x00\x00(r\x01\x02<\x00\xfb4\x9b'),
               bytearray(b'\x06\x01\x00B\x05\x00\x00%]\x01\x02<\x00\xfb4\x9b') ]:
    print("TEMP, ?, --, Fertility, ?, ?")
    le_data = unpack('<HBIBHHI', value)
    print("LE Data: " + str(le_data))
    print("--, --, Moisture, --, --, --")
    be_data = unpack('>HBIBHHI', value)
    print("BE Data: " + str(be_data))
    data = {
      'temperature': le_data[0]/10,
      'light': le_data[2],
      'moisture': be_data[3],
      'fertility': le_data[4]
    }
    print("Data: " + str(data))

