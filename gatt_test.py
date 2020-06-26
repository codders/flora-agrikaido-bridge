from struct import unpack
import gatt



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

        playback_manager = next((
            c for c in data_service.characteristics
            if c.uuid == '00001a10-0000-1000-8000-00805f9b34fb'), None)
        if playback_manager is None:
            print("No playback manager found")
        else:
            print("got playback manager")

#        realtime_data_characteristic.enable_notifications()
        firmware_characteristic.read_value()
        data_characteristic.enable_notifications()
#        playback_manager.enable_notifications()
        realtime_data_characteristic.write_value(bytearray([0xa0, 0x1f]))

 #       self.manager.stop_discovery()

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
            print("Data: " + str(data))

    def characteristic_write_value_succeeded(self, characteristic):
        print("Write succeeded for: %s" % characteristic.uuid)

    def characteristic_enable_notifications_succeeded(self, characteristic):
        print("Enabled notifications for %s" % characteristic.uuid)

    def characteristic_enable_notifications_failed(self, characteristic, error):
        print("Failed to enable notifications for %s" % characteristic.uuid, error)

    def disconnect_succeeded(self):
        super()
        print("Disconncted")

class AnyDeviceManager(gatt.DeviceManager):

    def __init__(self, adapter_name):
        super().__init__(adapter_name)
        self.devices = {}

    def device_discovered(self, device):
        if device.alias() == 'Flower care':
            print("Discovered [%s] %s" % (device.mac_address, device.alias()))
            self.stop_discovery()
            if device.mac_address not in self.devices:
                print("Creating flower")
                self.devices[device.mac_address] = AnyDevice(mac_address=device.mac_address, manager=self)
                self.devices[device.mac_address].connect()
            

manager = AnyDeviceManager(adapter_name='hci0')
manager.start_discovery()
manager.run()
