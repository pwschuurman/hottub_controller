# hottub_controller

This project is a hottub controller for an Aruba Spas controller. It was built with a Raspberry Pi Zero W.

## Overview

The Raspberry Pi sits on the line between the existing hot tub keypad and the hot tub controller. It operates as a passive sniffer (to read data being transmitted from the controller to the keypad's LEDs) and has control to act as a button, to simulate keypresses on the keypad.

## Technical Details

### Hardware

The hot tub controller is connected to the keypad with an 8-port connection, using 5v logic. The controller is a Motorola MC68HC912D60, running at 5V. The keypad uses a serial latch to read data via SPI and buffer it to the LEDs. This enables the controller to display different data on the keypad, depending on the state (eg: Displaying the current temperature, or the temperature that the hot tub is currently programmed to).

The pinout is the following:

| Description       | Pin |
| ----------------- | --- |
| Ground            | 1   |
| Temp Up           | 2   |
| Light             | 3   |
| Pump              | 4   |
| +5V               | 5   |
| Data In/Temp Down | 6   |
| Clock             | 7   |
| Enable            | 8   |

![Keypad](/readme/keypad.png)

#### Controller Inputs (Buttons)

Each of the buttons on the keypad correspond to a port. These are normally pulled up to high. When a button is pressed, these are drained low, with the following circuit:

[Resistor](/readme/button.png)

To drive these inputs, the Raspbery Pi operate a BJT switch, capable of driving the line low. The BJT selected (2N3904) has a CE voltage of 0.2 when fully saturated. According to the hot tub controller spec, voltage must be at most 1.0V, (0.2 * VCC), so this falls within the range. The BE voltage is 0.7 when saturated, providing 2.6V across the base resistor (Raspberry Pi provides 3.3V). A 2kOhm resistor was selected, allowing for a 1.3mA base current. The BJT has a gain of 10-20, allowing for the button circuit to drain 10-20mA, within spec.

Note that driving a button low requires the Raspberry Pi to drive a voltage high, as the BJT inverts the signal.

#### Controller Outputs (SPI)

The controller communicates to the keypad, sending it the status of the LEDs at ~60Hz. This protocol is sent over SPI mode 3 (CPHA=1, CPOL=1). These lines are spliced to a 74HC4050N high-to-low level shifter, allowing for the Raspberry Pi to safely sniff these signals as they change.

[Circuit Schematic](/readme/schematic.png)

### Software

The Raspberry Pi runs a tornado webserver that emulates a keypad. It uses the pigpio library to read data from and write data to the GPIO pins.

The controller transmits 4-bytes at ~60Hz, resulting in a bitrate of ~2KhZ. This is too fast for the Raspberry Pi to sniff using software polling, so hardware interrupts are used.

#### Protocol

The protocol 4-byte protocol contains the LED status (5-status LEDs, and 3 BCD digits for the 7 segment display).

| Byte 1   | Byte 2   | Byte 3   | Byte 4   |
| -------- | -------- | -------- | -------- |
| ----SSSS | S---AAAA | BBBBCCCC | -------- |

S = Status
A = Temperature (100's place)
B = Temperature (10's place)
C = Temperature (1's place)

#### References

Thanks to the following projects for providing the underlying infrastructure for the software:

[Pigpio][http://abyz.me.uk/rpi/pigpio/]
[Bitstring][https://github.com/scott-griffiths/bitstring]
[Tornado][https://www.tornadoweb.org/en/stable/]
[jQuery][https://jquery.com/]
