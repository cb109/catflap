import os
import time

# import esp
import machine
import network
from machine import Pin, Signal

try:
    import urequests as requests
except ImportError:
    import requests


# esp.sleep_type(esp.SLEEP_LIGHT)

SLEEP_MS = 333
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


def notify_server_about_catflap_opened_closed(config):
    query = """
        mutation {{
            createEvent(catflapId: {catflap_id}, kind: "OC") {{
                event {{
                    id
                    createdAt
                    kindLabel
                }}
            }}
        }}
    """.format(
        catflap_id=config["CATFLAP_ID"]
    )
    print("[INFO] Notifying server via API...")
    response = requests.post(config["API_URL"], json={"query": query})
    response.close()
    return response


def blink_led(seconds=0.25, times=1):
    for _ in range(times):
        led.on()
        time.sleep(seconds / 2.0)
        led.off()
        time.sleep(seconds / 2.0)


# State
# config = get_config()
# led = get_internal_led(config["INTERNAL_LED_PIN_INDEX"])
led = get_internal_led(2)
# sensor = get_sensor(config["SENSOR_PIN_INDEX"])
# previous_sensor_state = sensor.value()

# Connect to Wifi last, so we can blink when succeeding.
# wifi = connect_to_wifi(config)


def deepsleep(ms):
    if not "deepsleeped" in os.listdir():
        with open("deepsleeped", "w") as f:
            f.write("")

    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, ms)
    machine.deepsleep()


def woken_from_deepsleep():
    deepsleeped = "deepsleeped" in os.listdir()
    if deepsleeped:
        os.remove("deepsleeped")
    return deepsleeped


def loop_once():
    print("woken from deepsleep:", machine.reset_cause() == machine.DEEPSLEEP_RESET)
    print("sleeping now (2s to ctrl-c) ...")
    time.sleep(2)
    deepsleep(2000)


def loop_forever():
    while True:
        loop_once()


# loop_forever()
# loop_once()


def x():
    if woken_from_deepsleep():
        print("here I am again!")
    else:
        print("reset eh? going to sleep now")

    deepsleep(10000)


x()
