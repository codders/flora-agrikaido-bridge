# Flora Agrikaido Bridge

Script to post data from Xiaomi Flora devices to Agrikaido

## Requirements

The script is designed to run on a Linux machine with a Bluetooth (4+) adapter. You must have recent versions of `bluez` and `dbus` installed.

## Installation

Use [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today) to install the dependencies and start a shell:

```bash
pipenv install
```

If you have trouble building the native packages, make sure you have the development libraries for DBus, GObject and Cairo installed.

## Usage

The script is configured using environment variables. Specifically, you need an Agrikaido API token and Plot ID:

```bash
export API_TOKEN=<your_api_token>
export PLOT_ID=<your_plot_id>
```

Optionally, you can override the API URL by setting the `API_URL` environment variable.

You need to the run script as a user that has permissions on the `org.bluez` object of the system bus. You can add the following config to your `/etc/dbus-1/system.d/bluetooth.conf`:

```
<policy user="blePeripheral">
  <allow own="org.bluez"/>
  <allow send_destination="org.bluez"/>
  <allow send_interface="org.bluez.GattCharacteristic1"/>
  <allow send_interface="org.bluez.GattDescriptor1"/>
  <allow send_interface="org.freedesktop.DBus.ObjectManager"/>
  <allow send_interface="org.freedesktop.DBus.Properties"/>
</policy>
```

and restarting DBus (note that restarting DBus in a Desktop session will likely kill your window and network manager, and Bluez may need to be restarted).

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[AGPL-3.0](https://choosealicense.com/licenses/agpl-3.0/)
