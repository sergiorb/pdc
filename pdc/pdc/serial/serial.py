#!/usr/bin/python3
# -*- coding: utf-8 -*-

import serial, random, time, os, multiprocessing

from pdc.pdc import utils as pdc_utils
from pdc.pdc.serial import comm_protocol as cfg

class SerialDevice():

	_route_str = None
	_baud_rate = None
	_timeout = None
	_state = multiprocessing.Manager().Value('c_wchar_p','')
	_output_queue = multiprocessing.Queue(maxsize=0)
	_input_list =  multiprocessing.Manager().list()
	_comm_processes_list = []

	def __init__(self, route_str='/dev/ttyACM0', baud_rate=9600, timeout=10, 
		max_connection_attempts=5, time_between_attempts=5, log_path="./logs", 
		logging_level='debug'):
		"""
		Object instantiation method.
		"""

		self._log_path = log_path
		self._log_file = "%s/%s.log" % (self._log_path, __name__)
		self._logging_level = logging_level
		self._logger = pdc_utils.config_logger(__name__, self._log_file, logging_level=self._logging_level)

		self._route_str = route_str
		self._baud_rate = baud_rate
		self._timeout = timeout
		self._max_connection_attempts = max_connection_attempts
		self._time_between_attempts = time_between_attempts
		self._master_id = 0;
		self._ping_function_number = 0;

		self._state = 'INSTANTIATED'

		self._logger.debug("%s object instantiation" % __name__)

	def is_connected(self):

		if self._state == 'CONNECTED':

			return True

		else:

			return False

	def _get_response(self, orderStr):
		"""
		TODO: REVISE THIS FUNCTION AND ITS DEVICE RESPONSE
		"""

		orderStr = orderStr.decode()

		string = orderStr[orderStr.find(cfg.INITIALCHAR)+1:orderStr.find(cfg.STOPCHAR)]
		
		return string

	def _order_string_to_dict(self, order_string):
		"""
		"""

		try:
		
			iOc_position = order_string.find(cfg.IDENTIFIERCHART)
			fOc_position = order_string.find(cfg.STOPCHAR)
			id_ = order_string[1:iOc_position]
			response = order_string[iOc_position+1:fOc_position]

			return {

				"id": int(id_),
				"response": response
			}

		except Exception as e:

			self._logger.error(e);

			return None

	def _get_unique_id(self):
		"""
		Returns an unique order identifier.
		"""

		return random.randint(0,999999)

	def get_log(self):
		"""
		Returns a dictionary with log info and lines.
		"""

		return pdc_utils.get_log_dict(self.log_file)

	def get_device_info(self):
		"""
		Returns device information.
		"""

		return {
			"route": self._route_str,
			"baud_rate": self._baud_rate,
			"timeout": self._timeout,
			"max_connection_attempts": self._max_connection_attempts,
			"time_between_attempts": self._time_between_attempts,
			"state": self._state
		}

	def _open(self):
		"""
		Opens connection with serial device.
		"""

		# TODO: this should be threaded

		self._logger.info("Opening %s..." % self._route_str)

		try:

			self.device = serial.Serial(self._route_str, self._baud_rate, timeout=self._timeout)
			self._state = 'OPENED'

			self._logger.info("Opened %s. Baud rate: %d. _timeout: %d" 
				% (self._route_str, self._baud_rate, self._timeout))

		except serial.SerialException as e:

			self._state = 'NOT-OPENED'

			self._logger.error("Could not connect to %s. Baud rate: %d. _timeout: %d. Reason: %s" 
				% (self._route_str, self._baud_rate, self._timeout, e))
		
		if self._state == 'OPENED':

			self.device.flushInput()
			self.device.flushOutput()

			connection_attempts = 0

			self._state = 'CONNECTING'

			while self._state != 'READY' and connection_attempts < self._max_connection_attempts:

				connection_string = "%s%d%s%d%s" % (cfg.INITIALCHAR, self._master_id, cfg.DEFUSEPARATOR, self._ping_function_number, cfg.STOPCHAR)

				connection_string = connection_string.encode()

				self._logger.debug("Connection String: %s" % connection_string)

				self.device.write(connection_string)

				readed = self.device.readline()
				
				self._logger.debug("Readed: %s" % readed)

				response = self._get_response(readed)

				if(response == "ready"):

					self._state = 'READY'

					self._logger.info("%s ready!." % self._route_str)

					return True

				else:

					self._logger.warning("Connection attemp #%d failed!. Waiting %d" 
						% (connection_attempts, self._time_between_attempts))

					time.sleep(self._time_between_attempts)
				
				connection_attempts += 1

			if connection_attempts == self._max_connection_attempts:

				self._state = 'NOT-CONNECTED'

				self._logger.warning("Device %s opening failed!. Try to check connection and restart." % self._route_str)

		return False
		
	def _close(self):
		"""
		Stops and _close device connection.
		"""

		# TODO: Kill send_data and recieve_data loops
		
		#self.stop_run()
		self._state = 'CLOSED'
		self.device.flushInput()
		self.device.flushOutput()
		self.device.close()
		self._logger.info("Device %s closed." % self._route_str)

	def _send_data_loop(self, log_path, output_queue, logging_level):
		"""
		Reads orders from output queue and send them to serial.
		"""

		name = "send_data_loop"
		log_path = log_path + "/processes/serial/%s_%d.log" % (name, os.getpid())
		logger = pdc_utils.config_logger(name, log_path, logging_level=logging_level)

		logger.info("Initiated send data loop");

		while True:

			logger.debug("Waiting for new output order...")

			order = output_queue.get()

			to_device_string = "%s%d%s%d%s%d%s%s%s" % (cfg.INITIALCHAR, order["id"], cfg.IDENTIFIERCHART, order["device"], cfg.DEFUSEPARATOR, order["function"], cfg.DEFUSEPARATOR, order["data"], cfg.STOPCHAR)

			logger.info("To device string: %s" % to_device_string);

			self.device.write(to_device_string.encode())

	def _recieve_data_loop(self, log_path, input_list, logging_level):
		"""
		Reads serial input, creates data dicts and adds them to input queue.  
		"""

		name = "recieve_data_loop"
		log_path = log_path + "/processes/serial/%s_%d.log" % (name, os.getpid())
		logger = pdc_utils.config_logger(name, log_path, logging_level=logging_level)

		logger.info("Initiated send data loop")

		data_array = []
		string = ""
		receiving_data = False

		while True:
			
			logger.debug("Waiting for new bytes...")

			# Reads 1 byte from serial
			readed_data = self.device.read(1)

			readed_data = readed_data.decode()
			
			# If byte is Initial Order Chart or it is after Initial Order Chart...
			if(readed_data == cfg.INITIALCHAR or receiving_data == True):

				logger.debug("readed_data: %s" % readed_data)

				# Receiving order string for serial.
				receiving_data = True

				# Adds byte to array.
				data_array.append(readed_data)

				# If byte is Final Order Chart...
				if(readed_data == cfg.STOPCHAR):

					# No more bytes for current order string.
					receiving_data = False

					# Creates a string from byte array
					string = ''.join(data_array)

					# Resets byte array for new incoming orders.
					data_array = []

					logger.info("From device string: %s" % string)

					input_list.append(self._order_string_to_dict(string))
					
	def send_order(self, device, function, data="", register=False):
		"""
		Send Data to serial port.
		"""

		order_id = self._get_unique_id()

		if register:

			#self.outputStringsPoll.append([order_id, device, function, data])
			pass

		self._output_queue.put({

				"id": order_id,
				"device": device,
				"function": function,
				"data": data
			})

		return order_id

	def get_order_response(self, order_id):
		"""
		Retrieves data order from input list by order id.
		"""

		for order in self._input_list:

			if order["id"] == order_id:

				to_send_order = order
				
				self._input_list.remove(order)

				return to_send_order["response"]

		return None

	def connect(self):
		"""
		Runs device data-exchange processes.
		"""
		opened = self._open()

		if opened:

			try:

				# Creates process.
				send_data_p = multiprocessing.Process(
					target=self._send_data_loop, 
					args=(self._log_path, self._output_queue, 
						self._logging_level), 
					name="Device: Send data loop")

				recieve_data_p = multiprocessing.Process(
					target=self._recieve_data_loop,
					args=(self._log_path, self._input_list, 
						self._logging_level), 
					name="Device: Recieve data loop")
				
				# Stores communication processes pid's
				self._comm_processes_list.append(send_data_p)
				self._comm_processes_list.append(recieve_data_p)

				# Executes process.
				send_data_p.start()
				recieve_data_p.start()

				self._state = 'CONNECTED'

				return True

			except Exception as e:

				self._logger.error(e)
				self._close()

		return False

	def disconnect(self):

		if self._state == 'CONNECTED':

			pdc_utils.kill_processes_list(self._comm_processes_list)

			self._state == 'DISCONNECTED'

			self._close()

			return True

		return False
