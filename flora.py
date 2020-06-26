import dbus

bus = dbus.SystemBus();

obj = bus.get_object('org.bluez', '/org/bluez/hci0/dev_80_EA_CA_89_5C_32')

device = dbus.Interface(obj, 'org.bluez.Device1')

res = device.Connect()
print(res)
