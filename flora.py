import sys
import os
from struct import *
from binascii import hexlify

import gatt
import requests

from dotenv import load_dotenv

load_dotenv()

def ten_bit_signed(value):
    sign = '1' if value < 0 else '0'
    return sign + bin(abs(value))[2:].zfill(9)

def seven_bit_unsigned(value):
    return bin(abs(value & 0x3f))[2:].zfill(7)

def sample_url():
    env_url = os.getenv("API_URL")
    api_url = "https://beta.agrikaido.com/api" if env_url is None else env_url
    return api_url + "/samples?plot_id=" + os.getenv("PLOT_ID")

def post_result(mac_address, string):
    data = {
      "raw": string,
      "probe": {
        "serial": mac_address
      }
    }
    response = requests.post(sample_url(), json=data, headers={'Authorization': 'Bearer ' + os.getenv("API_TOKEN")})
    print(response.text)

# Agrikaido sensor data format
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
def convert_data_to_agrikaido_string(data):
    print("Data: " + str(data))
    bytes_data = bytearray(b'\x12\x01')
    binary_string = '';
    binary_string += ten_bit_signed(int(data['temperature'] * 10))
    binary_string += ten_bit_signed(int(data['temperature'] * 10))
    binary_string += '0000000' # Air humidity
    binary_string += '0000000000' # Soil temp
    binary_string += seven_bit_unsigned(data['moisture'])
    binary_string += '0000' 
    return "1201" + hex(int(binary_string, 2))[2:].zfill(12) + hex(data['light'])[2:].zfill(4) + '0000'

def post_dummy_data():
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
        data_string = convert_data_to_agrikaido_string(data)
        post_result("cafecafe", data_string)

class AnyDevice(gatt.Device):

    def __init__(self, mac_address, manager, managed=True):
        super().__init__(mac_address, manager, managed)

    def services_resolved(self):
        super().services_resolved()

        data_service = next(
            s for s in self.services
            if s.uuid == '00001204-0000-1000-8000-00805f9b34fb')

        realtime_data_characteristic = next(
            c for c in data_service.characteristics
            if c.uuid == '00001a00-0000-1000-8000-00805f9b34fb')

        firmware_characteristic = next(
            c for c in data_service.characteristics
            if c.uuid == '00001a02-0000-1000-8000-00805f9b34fb')

        data_characteristic = next(
            c for c in data_service.characteristics
            if c.uuid == '00001a01-0000-1000-8000-00805f9b34fb')

        firmware_characteristic.read_value()
        data_characteristic.enable_notifications()
        realtime_data_characteristic.write_value(bytearray([0xa0, 0x1f]))

    def characteristic_value_updated(self, characteristic, value):
        print("Characteristic: %s Value: " % characteristic.uuid, value)
        if characteristic.uuid == "00001a01-0000-1000-8000-00805f9b34fb":
            le_data = unpack('<HBIBHHI', value)
            be_data = unpack('>HBIBHHI', value)
            data = {
              'temperature': le_data[0]/10,
              'light': le_data[2],
              'moisture': be_data[3],
              'fertility': le_data[4]
            }
            post_result(self.mac_address, convert_data_to_agrikaido_string(data))

    def characteristic_write_value_succeeded(self, characteristic):
        print("Write succeeded for: %s" % characteristic.uuid)

    def characteristic_enable_notifications_succeeded(self, characteristic):
        print("Enabled notifications for %s" % characteristic.uuid)

    def characteristic_enable_notifications_failed(self, characteristic, error):
        print("Failed to enable notifications for %s" % characteristic.uuid, error)

    def disconnect_succeeded(self):
        super()
        print("Disconncted from sensor. Stopping")
        self.manager.stop()

class AnyDeviceManager(gatt.DeviceManager):

    def __init__(self, adapter_name):
        super().__init__(adapter_name)
        self.devices = {}

    def device_discovered(self, device):
        if device.alias() == 'Flower care':
            print("Discovered [%s] %s" % (device.mac_address, device.alias()))
            self.stop_discovery()
            if device.mac_address not in self.devices:
                print("Creating flower %s" % device.mac_address)
                self.devices[device.mac_address] = AnyDevice(mac_address=device.mac_address, manager=self)
                self.devices[device.mac_address].connect()


if __name__ == "__main__":
    if os.getenv("API_TOKEN") is None:
        print("Specify an Agrikaido API token with API_TOKEN environment variable")
        sys.exit(1)
    if os.getenv("PLOT_ID") is None:
        print("Specify an Agrikaido plot ID with PLOT_ID environment variable")
        sys.exit(1)
    manager = AnyDeviceManager(adapter_name='hci0')
    manager.start_discovery()
    manager.run()
