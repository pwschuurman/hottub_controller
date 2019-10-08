from fakebutton import FakeButton
from fakespiapi import FakeSpiAPI
from transmission import Transmission

import rx
from rx.subject import Subject

TEMP_UP_PIN = 10
TEMP_DOWN_PIN=13
LIGHT_PIN = 11
PUMP_PIN = 12

DATA_IN_PIN=17
CLOCK_PIN=18
ENABLE_PIN=19

class GpioAPI:
  def __init__(self, pi):
    # Setup buttons (Output)
    self.temp_down_button = Button(pi, TEMP_DOWN_PIN)
    self.temp_up_button = Button(pi, TEMP_UP_PIN)
    self.light_button = Button(pi, LIGHT_PIN)
    self.pump_button = Button(pi, PUMP_PIN)

    self.transmission_subject = Subject()

    # Setup input (data)
    self.spi_api = SpiAPI(pi, CLOCK_PIN, ENABLE_PIN, DATA_IN_PIN)
    self.spi_api.data.subscribe(on_next=self.callback)

  def callback(self, buffer):
    transmission = Transmission.parse(buffer)
    if transmission:
      self.transmission_subject.on_next(transmission)
