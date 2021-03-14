import time

from machine import Pin, Signal

INTERNAL_LED_PIN_INDEX = 2
SENSOR_PIN_INDEX = 4


def get_sensor(pin_index=SENSOR_PIN_INDEX):
    return Pin(pin_index, Pin.IN, Pin.PULL_UP)


def get_internal_led():
    return Signal(INTERNAL_LED_PIN_INDEX, Pin.OUT, invert=True)


# State
counter = 0
led = get_internal_led()
sensor = get_sensor()


while True:
    if sensor.value() == 0:
        print(str(counter) + " magnet detected!")
        led.on()
    else:
        print("")
        led.off()
    counter += 1
