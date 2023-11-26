import time
import logging
import pathlib
import subprocess

from olympus_wifi import OlympusCamera
from olympus_wifi.network_manager import WifiConnection

adapter_name = "wlan0"
ssid = 'WIFI_SSID'
password = 'WIFI_PSK'

logging.basicConfig(level=logging.DEBUG)

with WifiConnection(device_name=adapter_name, ssid=ssid, psk=password):
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
