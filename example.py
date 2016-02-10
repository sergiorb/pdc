# -*- coding: utf-8 *-*

import time

from comm.serialDevice import SerialDevice

class App():
	"""
		Example app class for using PDC
	"""

	def __init__(self, device=None):

		self.device = device


	def hello(self, my_name='PACOLAND', timeout=10, refresh_rate=1):
		"""
			Sends a given name to the serial device
		"""
		response = None
		guard = 0

		if self.device.is_ready:
			orderID = self.device.send_data(register=True, device=0, function=6, data=my_name)
			
			while not response and guard < timeout:
				response = self.device.getResponse(orderID)
				time.sleep(refresh_rate)
				guard = guard + refresh_rate

			return response

		else:
			self.log.warning("Device not ready.")



outputDevice = SerialDevice(routeStr='/dev/ttyACM0', name="My personal serial device", logLevel=2)
app = App(device=outputDevice)


outputDevice.open()
outputDevice.start()

print app.hello()

outputDevice.close()


