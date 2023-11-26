import time
import enum
import functools
import logging

logger = logging.getLogger(__name__)

import dbus

class DbusObject:
    def __init__(self, bus, path, api_path=None):
        self.bus = bus
        self.path = path

        bus_name = "org.freedesktop.NetworkManager"
        self.object = bus.get_object(bus_name=bus_name, object_path=path)

        api_path = api_path or path.replace("/", ".").lstrip(".")
        self.method_if = dbus.Interface(object=self.object, dbus_interface=api_path)
        self.properties_if = dbus.Interface(
            object=self.object, dbus_interface="org.freedesktop.DBus.Properties")

    def get_property(self, name):
        return self.properties_if.Get("org.freedesktop.NetworkManager.Device", name)

class NetworkDevice:
    class NMDeviceType(enum.Enum):
        # https://people.freedesktop.org/~lkundrak/nm-docs/nm-dbus-types.html#NMDeviceType
        UNKNOWN = 0
        GENERIC = 14
        ETHERNET = 1
        WIFI = 2
        BRIDGE = 13
        UNKNOWN2 = 30
        # TODO: missing items

    class NMDeviceState(enum.Enum):
        # https://people.freedesktop.org/~lkundrak/nm-docs/nm-dbus-types.html#NMDeviceState
        UNKNOWN = 0
        UNMANAGED = 10
        UNAVAILABLE = 20
        DISCONNECTED = 30
        PREPARE = 40
        CONFIG = 50
        NEED_AUTH = 60
        IP_CONFIG = 70
        IP_CHECK = 80
        SECONDARIES = 90
        ACTIVATED = 100
        DEACTIVATING = 110
        FAILED = 120

    def __init__(self, bus, device_path):
        self.path = device_path
        self.device = DbusObject(
            bus, device_path, "org.freedesktop.NetworkManager.Device")

    def __repr__(self):
        return f"{self.name} - {self.state} - {self.type} - {self.mac}"

    @functools.cached_property
    def mac(self):
        if self.type in [self.NMDeviceType.ETHERNET, self.NMDeviceType.WIFI]:
            return self.device.get_property("HwAddress")
        return None

    @functools.cached_property
    def type(self):
        return self.NMDeviceType(
            self.device.get_property("DeviceType"))

    @functools.cached_property
    def name(self):
        return self.device.get_property("Interface")

    @property
    def state(self):
        return self.NMDeviceState(
            self.device.get_property("State"))

    def disconnect(self):
        logger.debug(f"Disconnecting {self.name}")
        self.device.method_if.Disconnect()

class WifiConnection:
    def __init__(self, device_name, ssid, psk):
        self.ssid = ssid
        self.psk = psk

        self.bus = dbus.SystemBus()

        self.nm = DbusObject(
            self.bus, "/org/freedesktop/NetworkManager")
        self.nm_settings = DbusObject(
            self.bus, "/org/freedesktop/NetworkManager/Settings")
        self.nm_devices_list = [
            NetworkDevice(self.bus, dpath) for dpath in self.nm.method_if.GetDevices()]

        # Find device
        for device_path in self.nm.method_if.GetDevices():
            self.device = NetworkDevice(self.bus, device_path)
            if self.device.name == device_name:
                break
        else:
            raise KeyError(f"Cannot find {device_name=}")

        self.new_connection_path = None
        self.new_connection = None
        self.new_connection_if = None

    def is_connected(self):
        return self.device.state == NetworkDevice.NMDeviceState.ACTIVATED

    def wait_connected(self):
        while not self.is_connected():
            time.sleep(0.5)

    def is_disconnected(self):
        return self.device.state == NetworkDevice.NMDeviceState.DISCONNECTED

    def wait_disconnected(self):
        while not self.is_disconnected():
            time.sleep(0.5)

    def delete_connection(self):
        self.new_connection.method_if.Delete()

    def connect(self):
        logger.debug(f"Connecting {self.device.name} to {self.ssid}")
        mac_address = dbus.ByteArray(bytes.fromhex(self.device.mac.replace(':', '')))
        connection = {
            'connection': {
                'id': self.ssid,
                'type': '802-11-wireless',
                'autoconnect': True
            },
            '802-11-wireless': {
                'mode': 'infrastructure',
                'ssid': dbus.ByteArray(self.ssid.encode('utf8')),
                'mac-address': mac_address,
            },
            '802-11-wireless-security': {
                'key-mgmt': 'wpa-psk',
                'psk': self.psk,
            },
            'ipv4': {'method': 'auto'},
        }

        new_connection_path = \
            self.nm_settings.method_if.AddConnectionUnsaved(connection)

        self.new_connection = DbusObject(
            self.bus, new_connection_path, "org.freedesktop.NetworkManager.Settings.Connection")

        self.nm.method_if.ActivateConnection(
            self.new_connection.path, self.device.path, "/")

    def __enter__(self):
        if self.is_connected():
            logger.warning("Disconnecting active connection")
            self.device.disconnect()
            self.wait_disconnected()

        if not self.is_disconnected():
            raise RuntimeError(f"{self.device.name} is still connected")

        self.connect()
        self.wait_connected()

    def __exit__(self, *args, **kwargs):
        self.device.disconnect()
        self.wait_disconnected()
        self.delete_connection()
