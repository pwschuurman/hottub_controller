from gpioapi import GpioAPI

import rx

MAX_TEMP = 38
COOL_TEMP = 30

class HotTubAPI:
  def __init__(self):
    self.gpioapi = GpioAPI(None)

  def transmissions(self):
    return self.gpioapi.transmission_subject

  def heat_up(self):
    reached_max_temp = self.gpioapi.transmission_subject.pipe(
      op.filter(lambda x: x.set_point() is not None and x.set_point() >= MAX_TEMP)
    )

    # Press the temp-up button until reached max temp
    rx.interval(1.0).pipe(
      op.timeout(15.0),
      op.take_until(reached_max_temp)
    ).on_next(self.press_temp_up_button())

  def cool_down(self):
    reached_cool_temp = self.gpioapi.transmission_subject.pipe(
      op.filter(lambda x: x.set_point() <= COOL_TEMP)
    )

    # Press the temp-up button until reached cool temp
    rx.interval(1.0).pipe(
      op.timeout(15.0),
      op.take_until(reached_cool_temp)
    ).on_next(self.press_temp_down_button())

  
  def press_light_button(self):
    self.gpioapi.light_button.press()

  def press_pump_button(self):
    self.gpioapi.pump_button.press()

  def press_temp_down_button(self):
    self.gpioapi.temp_down_button.press()

  def press_temp_up_button(self):
    self.gpioapi.temp_up_button.press()
