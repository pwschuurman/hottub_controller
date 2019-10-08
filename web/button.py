class Button:
	def __init__(self, pi, gpio):
		self.pi = pi

		pi.set_mode(gpio, pigpio.OUTPUT)
		pi.wave_clear()
		pi.wave_add_generic([pigpio.pulse(1<<gpio, 1<<gpio, 100000)]) # 100ms
		self.wave_id = pi.wave_create()

	def __del__(self):
		self.pi.wave_delete(self.wave_id)

	def press_button(self):
		self.pi.wave_send_once(self.wave_id)
