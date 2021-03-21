import os
import time

import network
from machine import Pin, Signal

INTERNAL_LED_PIN_INDEX = 2
SENSOR_PIN_INDEX = 4


def get_config(filepath=".env"):
    config = {
        "WIFI_SSID": None,
        "WIFI_PSK": None,
    }
    try:
        handle = open(filepath)
    except OSError:
        print("[WARN] No config file found at: " + filepath)
        return config

    for line in handle.readlines():
        if line.strip() == "":
            continue
        try:
            key, value = line.split("=")
        except ValueError:
            print("[WARN] Unreadable config line: " + line)
            continue
        key, value = key.strip(), value.strip()
        config[key] = value

    return config


def get_sensor(pin_index=SENSOR_PIN_INDEX):
    return Pin(pin_index, Pin.IN, Pin.PULL_UP)


def get_internal_led():
    return Signal(INTERNAL_LED_PIN_INDEX, Pin.OUT, invert=True)


def connect_to_wifi(config):
    # See:
    # - https://docs.micropython.org/en/latest/esp8266/tutorial/network_basics.html
    # - https://docs.micropython.org/en/latest/esp8266/quickref.html#networking

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if not wifi.isconnected():

        ssid = config["WIFI_SSID"]
        psk = config["WIFI_PSK"]
        if not ssid and psk:
            print("[WARN] No wifi credentials in config, cannot connect")
            return False

        print("[INFO] Connecting to wifi " + ssid + " ...")
        wifi.connect(ssid, psk)
        while not wifi.isconnected():
            pass

    print("[INFO] Wifi is connected: " + str(wifi.isconnected()))
    return wifi


def blink_led(seconds=0.25, times=1):
    for _ in range(times):
        led.on()
        time.sleep(seconds / 2.0)
        led.off()
        time.sleep(seconds / 2.0)


config = get_config()
wifi = connect_to_wifi(config)

led = get_internal_led()
sensor = get_sensor()

previous_sensor_state = sensor.value()

# if wifi.isconnected():
#     blink_led(seconds=1.0, times=2)
# else:
#     blink_led(seconds=0.1, times=5)

while True:
    sensor_state = sensor.value()

    has_changed = sensor_state != previous_sensor_state
    if not has_changed:
        continue

    blink_led()
    previous_sensor_state = sensor_state

