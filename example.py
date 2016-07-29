#!/usr/bin/python3
# -*- coding: utf-8 *-*

import time

from pdc.serial.serial import SerialDevice

print("PDC example.")
serial_device = SerialDevice(route_str='/dev/ttyACM0')

print("Connecting...")
serial_device.connect()

if serial_device.is_connected():

	order_id = serial_device.send_order(device=0, function=5, data=input('What is yout name?\n'))

	time.sleep(0.5)

	response = serial_device.get_order_response(order_id)

	serial_device.disconnect()

	print('Device response: {response}'.format(response=response))

else:

	print("Device can't connect!. Check out the logs for more info.")
