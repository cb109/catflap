import time

from machine import Pin, Signal

INTERNAL_LED_PIN_INDEX = 2
SENSOR_PIN_INDEX = 4


def get_sensor(pin_index=SENSOR_PIN_INDEX):
    return Pin(pin_index, Pin.IN, Pin.PULL_UP)


def get_internal_led():
    return Signal(INTERNAL_LED_PIN_INDEX, Pin.OUT, invert=True)


def blink_led(seconds=0.25):
    led.on()
    time.sleep(seconds)
    led.off()


led = get_internal_led()
sensor = get_sensor()

previous_sensor_state = sensor.value()


while True:
    sensor_state = sensor.value()

    has_changed = sensor_state != previous_sensor_state
    if not has_changed:
        continue

    blink_led()
    previous_sensor_state = sensor_state

