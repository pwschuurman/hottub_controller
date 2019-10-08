from collections import namedtuple
import bitstring

Packet = namedtuple('Packet', 'temp_led light_led heat_led heater_led pump_led temperature')

class Transmission(Packet):
  def set_point():
  	"""Retrieves the set_point, if available."""
    if temp_led and temperature != 0:
      return temperature
    else:
      return None

  def current_temperature():
  	"""Retrieves the current temperature, if available."""
    if not temp_led and temperature != 0:
      return temperature
    else:
      return None

  def parse(buffer):
    """Parses a bitstring to a Transmission object

    Format of the 4-byte string

    |=======================================================|
    | XXXX | SSSS | SXXX | TTTT | TTTT | TTTT | XXXX | XXXX |
    |=======================================================|
    | X = unused
    | S = Status bits
    | T = Temperature bits
    
    Status is 5 bits, corresponding to the LEDs on the display:
     * temp_led: Enabled when the set point temperature is currently displayed
     * light_led: Enabled when the hot tub light is on
     * heat_led: Enabled when the hot tub is above 20 degrees?
     * heater_led: Enabled when the heater is on
     * pump_led: Enabled when the pump is on

    Temperature is 3 BCD encoded digits

    Args:
      buffer: A bitstring
    """
    if buffer.length == 32:
      temp_led, light_led, heat_led, heater_led, pump_led, t1, t2, t3 = buffer.unpack('pad:4, bool:1, bool:1, bool:1, bool:1, bool:1, pad:3, uint:4, uint:4, uint:4, pad:8')
      temp = t1 * 100 + t2 * 10 + t3
      return Transmission(
        temp_led=temp_led,
        light_led=light_led,
        heat_led=heat_led,
        heater_led=heater_led,
        pump_led=pump_led,
        temperature=temp)
