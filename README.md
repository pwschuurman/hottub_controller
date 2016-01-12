# hottub_controller

This project is a hottub controller for an Aruba Spas controller. It was built with an Attiny85 + Raspberry Pi.

Two folders:
* avr/
  Contains code for accepting data requests from the Raspberry Pi via SPI, and modifying/fetching the
  hottub temperature and status via I2C.
  
* web/
  Contains a python webserver that hosts an emulated control panel (same UI as the physical keypad on the
  hot tub) for the hot tub.
