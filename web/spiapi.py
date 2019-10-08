from rx.subject import Subject
import pigpio
import bitstring

class SpiAPI:
	def __init__(self, pi, clock, enable, data_in):
		self.pi = pi

    pi.set_mode(clock, pigpio.INPUT)
    pi.set_mode(enable, pigpio.INPUT)
    pi.set_mode(data_in, pigpio.INPUT)

    self.clock_callback = pi.callback(clock, pigpio.RISING_EDGE, self.clock_toggle)
    self.enable_callback = pi.callback(enable, pigpio.EDGE_EITHER, self.enable_toggle)
    self.data_in_callback = pi.callback(data_in, pigpio.EDGE_EITHER, self.data_in_toggle)

    # Read the first bit
    self.data_in_bit = pi.read(data_in)

    self.buffer = bitstring.BitStream()

    self.spi_subject = Subject()

  def __del__(self):
  	self.clock_callback.cancel()
  	self.enable_callback.cancel()
  	self.data_in_callback.cancel()

  def clock_toggle(self, gpio, level, tick):
  	# Rising Edge: data_in has valid data
  	self.buffer.append('bool', self.data_in_bit)

  def enable_toggle(self, gpio, level, tick):
  	# Falling Edge: Start of transmission
  	# Rising Edge: End of transmission
  	if level == 1:
  		self.spi_subject.on_next(self.buffer.copy())
  	self.buffer.clear()

  def data_in_toggle(self, gpio, level, tick):
  	self.data_in_bit = level
