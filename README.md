# catflap

## Useful collections of tips regarding MicroPython on a Wemos D1 Mini

http://www.mark-fink.de/2020-03-24-micropython-on-esp8266/

## Install the firmware

- Download firmware from: http://micropython.org/download/esp8266/
- Then follow: http://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#deploying-the-firmware

Lower baudrate of 115200 can help to prevent flashing problems.

    $ sudo usermod -a -G dialout <user>
    # did not work for me, so sudo instead

    $ sudo esptool.py --port /dev/ttyUSB0 erase_flash
    $ sudo esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash --flash_size=detect 0 ~/Downloads/esp8266-20200911-v1.13.bin

## REPL

See: http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html

    $ sudo apt-get install picocom
    $ sudo picocom -b 115200 -r -l /dev/ttyUSB0


## Making an LED blink

Connect LED on breadboard with GND and any Pin e.g. D2 (aka Pin 4), with an e.g. 470 Ohm resistor in between the LED and GND.

Toggle like this:

    >>> from machine import Pin
    >>> led = machine.Pin(4, machine.Pin.OUT)
    >>> led.on()
    >>> led.off()

## Client Development

- `$ pip install adafruit-ampy`
- List files on board: `$ ampy --port /dev/ttyUSB0 ls`
- Copy file to board: `$ ampy --port /dev/ttyUSB0 put main.py`

### Install MicroPython libraries

- Open a shell to the board
- Within the REPL type:

    ```python
    >>> import upip
    >>> upip.install("micropython-uasyncio")
    ```

## Read A3144 Hall Effect Sensor Value

### Pinout

Slanted front facing you:

```
____________
|           |
|___________|
\___________/
 |    |    |

 5V  GND  OUT
```

### Connect to Wemos D1 Mini Pins

```
 5V   G    D2 (aka Pin No. 4)
```

### Read Sensor

    >>> from machine import Pin
    >>> sensor = Pin(4, Pin.IN, Pin.PULL_UP)
    >>> while True:
    >>>     if sensor.value() == 0:
    >>>         print("magnet detected!")
    >>>     else:
    >>>         print("")
    >>>
