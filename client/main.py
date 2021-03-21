import os
import time

import network
from machine import Pin, Signal

default_config = {
    "SENSOR_PIN_INDEX": 4,
    "INTERNAL_LED_PIN_INDEX": 2,
    "WIFI_SSID": None,
    "WIFI_PSK": None,
}


def get_config(filepath=".env"):
    # Defaults
    config = dict(default_config)
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


def get_sensor(pin_index):
    return Pin(pin_index, Pin.IN, Pin.PULL_UP)


def get_internal_led(pin_index):
    return Signal(pin_index, Pin.OUT, invert=True)


def connect_to_wifi(config, timeout_seconds=10):
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

        interval = 0.5
        time_left = timeout_seconds
        while not wifi.isconnected():
            if time_left <= 0:
                blink_led(times=5)
                return None
            time.sleep(interval)
            time_left -= interval

    blink_led()
    print("[INFO] Wifi is connected: " + str(wifi.isconnected()))
    return wifi


def blink_led(seconds=0.15, times=1):
    for _ in range(times):
        led.on()
        time.sleep(seconds / 2.0)
        led.off()
        time.sleep(seconds / 2.0)


# State
config = get_config()
led = get_internal_led(config["INTERNAL_LED_PIN_INDEX"])
sensor = get_sensor(config["SENSOR_PIN_INDEX"])
previous_sensor_state = sensor.value()

# Connect to Wifi last so we can blink if succeeding
wifi = connect_to_wifi(config)

while True:
    sensor_state = sensor.value()

    has_changed = sensor_state != previous_sensor_state
    if not has_changed:
        continue

    blink_led()
    previous_sensor_state = sensor_state

