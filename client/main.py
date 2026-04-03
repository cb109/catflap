import os
import time

import esp
import machine
import network
from machine import Pin, Signal

try:
    import urequests as requests
except ImportError:
    import requests


esp.sleep_type(esp.SLEEP_LIGHT)

SLEEP_MS = 50
EVENT_OPENED_CLOSED = "OC"

default_config = {
    # Hardware internals
    "SENSOR_PIN_INDEX": 4,
    "INTERNAL_LED_PIN_INDEX": 2,
    "CATFLAP_CLOSED_SENSOR_STATE": 1,
    # Configuration
    "API_URL": None,
    "CATFLAP_ID": 1,
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
        if value in ("0", "1"):
            value = int(value)
        config[key] = value

    return config


def get_sensor(pin_index):
    return Pin(int(pin_index), Pin.IN, Pin.PULL_UP)


def get_internal_led(pin_index):
    return Signal(int(pin_index), Pin.OUT, invert=True)


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


def notify_server_about_catflap_opened_closed(config, duration=None):
    catflap_id = catflap_id = config["CATFLAP_ID"]
    optional_duration = (
        "duration: {duration}".format(duration=duration) if duration is not None else ""
    )
    query = """
        mutation {{
            createEvent(
                catflapId: {catflap_id},
                kind: "OC",
                {optional_duration}
            ) {{
                event {{
                    id
                    createdAt
                    kindLabel
                }}
            }}
        }}
    """.format(
        catflap_id=catflap_id, optional_duration=optional_duration
    )
    print("[INFO] Notifying server via API...")
    response = requests.post(config["API_URL"], json={"query": query})
    response.close()
    return response


def blink_led(seconds=0.1, times=1):
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
previous_sensor_timestamp = time.ticks_ms()

# Connect to Wifi last, so we can blink when succeeding.
wifi = connect_to_wifi(config)


def loop_once():
    global previous_sensor_state
    global previous_sensor_timestamp

    sensor_state = sensor.value()
    has_changed = sensor_state != previous_sensor_state
    if not has_changed:
        pass
    else:
        is_closed = sensor_state == config["CATFLAP_CLOSED_SENSOR_STATE"]
        if is_closed:
            duration = None
            if previous_sensor_timestamp:
                # Compute time in seconds.
                duration = (
                    time.ticks_diff(time.ticks_ms(), previous_sensor_timestamp) / 1000
                )
                previous_sensor_timestamp = None

            notify_server_about_catflap_opened_closed(config, duration=duration)
            print("[INFO] Catflap has been closed |")
        else:
            print("[INFO] Catflap has been opened \\")
            previous_sensor_timestamp = time.ticks_ms()

        blink_led()
        previous_sensor_state = sensor_state

    machine.lightsleep(SLEEP_MS)


def loop_forever():
    while True:
        loop_once()


loop_forever()
