# -*- coding: utf-8 *-*

from Device import SerialDevice

outputDevice = SerialDevice(routeStr='/dev/ttyAMA0', name="My personal serial device", logLevel=2)

outputDevice.open()
outputDevice.start()