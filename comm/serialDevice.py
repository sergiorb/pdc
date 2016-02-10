# -*- coding: utf-8 *-*

import threading, serial, random, time
import logging, sys

from Queue import Queue

from .tools import threaded

class SerialDevice(threading.Thread):
	"""
	Handles serial device communication.
	"""
	name = None
	routeStr = None
	baudRate = None
	timeout = None
	ready = False
	serialObj = None
	runControler = False
	eventHandler = None
	inputStringsPoll = []
	outputStringsPoll = []
	toSendQueue = Queue(maxsize=0)
	SERVER_PORT = 80
	# Inital char for detecting incoming order's String.
	INITIALCHAR = '$'
	#
	IDENTIFIERCHART = ":"
	# device Id and function separator in order's String.
	DEFUSEPARATOR = '/'
	# Variable separator
	VARSEPARATOR = '&'
	# Final char for detecting the final order's string.
	STOPCHAR = ';'

	def __init__(self, routeStr, baudRate=9600, timeout=10, eventHandler=None, name="Device Unknow", logLevel=0, logfile='server.log'):
		threading.Thread.__init__(self)
		self.routeStr = routeStr
		self.baudRate = baudRate
		self.timeout = timeout
		self.eventHandler = eventHandler

		logging.basicConfig(filename=logfile, format='%(asctime)s ||TYPE:%(levelname)s ||FROM: %(name)s ||MSG: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
		self.log = logging.getLogger(name)

		if(logLevel==0):
			self.log.setLevel(logging.INFO)
			self.log.info("Level set to 0-INFO")
		elif(logLevel==1):
			self.log.setLevel(logging.WARNING)
			self.log.info("Level set to 1-WARNING")
		elif(logLevel==2):
			self.log.setLevel(logging.DEBUG)
			self.log.info("Level set to 2-DEBUG")
		else:
			self.log.setLevel(logging.DEBUG)
			self.log.info("Level set to 2-DEBUG")


		self.log.info("Device instance created. Route: %s" % routeStr)

	def inStringsChopper(self, message):
		if(message[0] == self.INITIALCHAR and message[-1] == self.STOPCHAR):
			idenPos = message.find(self.IDENTIFIERCHART)
			stopPos = message.find(self.STOPCHAR)
			stringId = message[1:idenPos]
			response = message[idenPos+1:stopPos]
			try:
				return [int(stringId), response]
			except:
				self.log.error("ERROR: "+stringId)
		else:
			return None

	def open(self):
		"""
			Opens the communication with serial device.
		"""
		self.log.info("Opening %s..." % self.routeStr)
		opened = False

		try:
			self.serialObj = serial.Serial(self.routeStr, self.baudRate, timeout=self.timeout)
			opened = True
		except serial.SerialException, e:
			self.log.error("Could not open port. Reason: %s" % e)

		if opened:
			# Cleans in/out on serial.
			self.serialObj.flushInput()
			self.serialObj.flushOutput()

			counter = 0

			while True:

				# Sends a heart beat signal to check if device is connected and ready.
				self.log.debug("%s0%s0%s" % (self.INITIALCHAR,self.DEFUSEPARATOR,self.STOPCHAR))
				self.serialObj.write("%s0%s0%s" % (self.INITIALCHAR,self.DEFUSEPARATOR,self.STOPCHAR))
				readed = self.serialObj.readline()
				self.log.debug("Readed: "+readed)

				# If device is ready.
				if(self.stringFilter(readed)=="ready"):
					self.ready = True
					self.log.info("%s opened." % self.routeStr)
					break
				else:
					self.log.warning("Failed!")
					self.log.warning("Waiting %s" % str(self.timeout))
					time.sleep(self.timeout)
					self.log.warning("Trying again...")

					# Exits if tried more the 5 times.
					if counter == 5:
						self.log.warning("Device %s opening failed!. Try to check connection and restart." % self.routeStr)
						break
					counter += 1
		

	def is_ready(self):
		"""
		Returns true is communication with serial device is alive.
		"""
		return self.ready

	def close(self):
		"""
		Close contection with device.
		"""

		self.log.info("Trying to close %s device" % self.routeStr)
		self.stop()

		self.serialObj.close()
		self.ready = False
		self.log.info("Device %s closed." % self.routeStr)

	def stringFilter(self, orderStr):
		return orderStr[orderStr.find(self.INITIALCHAR)+1:orderStr.find(self.STOPCHAR)]

	@threaded
	def send_data_loop(self):
		"""
		Searchs for task in toSendQueue and send it to the device.
		"""
		if self.ready:

			while self.runControler:

				if self.toSendQueue.qsize() > 0:
					orderStr = self.toSendQueue.get(timeout=5)
					self.log.debug("Sending Function '%s', Data: '%s' to %s." % (orderStr[2], orderStr[3], self.routeStr))

					try:
						self.log.debug("Sending %s" % self.INITIALCHAR+str(orderStr[0])+self.IDENTIFIERCHART+str(orderStr[1])+self.DEFUSEPARATOR+str(orderStr[2])+self.DEFUSEPARATOR+str(orderStr[3])+self.STOPCHAR)
						self.serialObj.write(self.INITIALCHAR+str(orderStr[0])+self.IDENTIFIERCHART+str(orderStr[1])+self.DEFUSEPARATOR+str(orderStr[2])+self.DEFUSEPARATOR+str(orderStr[3])+self.STOPCHAR)
					except IOError, e:
						self.log.error("Couldnt send data to device. %s" % e)
					except Exception, e:
						self.ready = False
						self.log.error("ERROR: %s" % e)
					finally:
						self.toSendQueue.task_done()
			self.log.info("Data send loop stop for device %s" % self.routeStr)

	def send_data(self, device, function, data="", register=False):
		"""
		Puts on toSendQueue a task and returns its ID.
		If register is true, the method appends the task to outputStringsPoll to
		allow programs track if task is processed or not.
		"""

		if self.ready:
			orderID = self.getOrderId()

			if(register):
				self.outputStringsPoll.append([orderID, device, function, data])

			self.toSendQueue.put([orderID, device, function, data])
			self.log.debug("OUTPUTSTRINGSPOLL: "+str(self.outputStringsPoll))
			return orderID
		else:
			self.log.warning("Could not send data over %s. Device not READY!" % self.routeStr)
			return None

	def getOrderId(self):
		"""
		Generates an unique ID for tasks.
		"""
		randNumber = None
		repeat = True

		while repeat:
			repeat = False
			randNumber = random.randint(0,999999)

			for x in range(0,len(self.outputStringsPoll)):
				if(self.outputStringsPoll[x][0] == randNumber):
					repeat = True
					break
			if not repeat:
				for x in range(0,len(self.inputStringsPoll)):
					if(self.inputStringsPoll[x][0] == randNumber):
						repeat = True
						break
		return randNumber

	def getResponse(self, stringId):
		"""
		Retrieves data from processed task at inputStringsPoll.
		"""

		for x in range(0, len(self.inputStringsPoll)):
			if(self.inputStringsPoll[x][0] == stringId):
				data = self.inputStringsPoll[x][1]
				self.searchCleanInOutPoll(stringId)
				return data

	def searchCleanInOutPoll(self, stringId):
		"""
		Cleans input/output polls of stringId.
		"""
		for x in range(0,len(self.outputStringsPoll)):
			if(self.outputStringsPoll[x][0] == stringId):
				del self.outputStringsPoll[x]
				break
		for x in range(0,len(self.inputStringsPoll)):
			if(self.inputStringsPoll[x][0] == stringId):
				del self.inputStringsPoll[x]
				break

	def run(self):
		"""
		Crawls data strings from serial input, searching INITIALCHAR and STOPCHAR.
		"""
		self.runControler = True
		self.send_data_loop()
		dataArray = []
		string = ""
		incomingData = False

		if self.ready:

			self.log.info("Device %s running." % self.routeStr)

			while self.runControler:

				try:
					data = self.serialObj.read(1)
				except Exception, e:
					self.ready = False
					self.runControler = False
					self.log.error(e)
				
				if(data == self.INITIALCHAR or incomingData == True):
					dataArray.append(data)
					incomingData = True
					if(data == self.STOPCHAR):
						incomingData = False
						string = ''.join(dataArray)
						dataArray = []
						self.log.debug("Device %s send '%s'." % (self.routeStr, string))
						self.inputStringsPoll.append(self.inStringsChopper(string))
						self.log.debug("INPUTSTRINGSPOLL" + str(self.inputStringsPoll))

			self.log.info("Device %s stop running." % self.routeStr)
		else:
			self.log.info("Device %snot ready" % self.routeStr)

	def stop(self):
		"""
		Stops device.
		"""
		self.log.info("Trying to stop device %s" % self.routeStr)
		self.runControler = False