import logging, os, errno

LOG_FORMAT_STRING = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def mkdir_p(path):
	"""
	http://stackoverflow.com/a/600612/190597 (tzot)
	"""

	try:
		os.makedirs(path, exist_ok=True)  # Python>3.2
	except TypeError:
		try:
			os.makedirs(path)
		except OSError as exc: # Python >2.5
			if exc.errno == errno.EEXIST and os.path.isdir(path):
				pass
			else: raise


class MakeFileHandler(logging.FileHandler):
	"""
	http://stackoverflow.com/a/20667049
	"""

	def __init__(self, filename, mode='a', encoding=None, delay=0):            
	
		mkdir_p(os.path.dirname(filename))
		logging.FileHandler.__init__(self, filename, mode, encoding, delay)


def create_file_handler(log_file, handler_level, formatter=logging.Formatter(LOG_FORMAT_STRING)):
	"""
	Creates file handler which logs even debug messages.
	"""

	if handler_level == 'debug':
		level = logging.DEBUG

	elif handler_level == 'info':
		level = logging.INFO

	elif handler_level == 'warning':
		level = logging.WARNING

	elif handler_level == 'error':
		level = logging.ERROR

	elif handler_level == 'critical':
		level = logging.CRITICAL

	else:

		raise Exception('logger level has to be defined')

	fh = MakeFileHandler(log_file)
	fh.setLevel(level)
	fh.setFormatter(formatter)

	return fh

def config_logger(name, log_file, formatter=logging.Formatter(LOG_FORMAT_STRING), logging_level='debug'):
	"""
	Returns logger object
	"""

	logger = logging.getLogger(name)

	if logging_level == 'debug':
		logger.setLevel(logging.DEBUG)

	elif logging_level == 'info':
		logger.setLevel(logging.INFO)

	elif logging_level == 'warning':
		logger.setLevel(logging.WARNING)

	elif logging_level == 'error':
		logger.setLevel(logging.ERROR)

	elif logging_level == 'critical':
		logger.setLevel(logging.CRITICAL)

	else:

		raise Exception('logger level has to be defined')

	# add the handlers to the logger
	
	logger.addHandler(create_file_handler(log_file, logging_level, formatter))

	return logger

def log_line_to_dict(line, separator):
	"""
	Transforms a log line to a dict
	"""

	# TODO: This function should be based on
	# LOG_FORMAT_STRING

	data_dict = {}

	# Labels array has to match LOG_FORMAT_STRING elemtens.
	labels = ["asctime", "name", "levelname", "message"]
	data = line.split(separator)

	for element in zip(labels, data):
		data_dict[element[0]] = element[1]

	return data_dict

def get_log_dict(log_file):
	"""
	Transform a log file to dict.
	"""

	log_dict = {
		"file": log_file,	
		"lines": []
	}

	try:

		f = open(log_file, 'r')

		for line in f.readlines():

			log_dict["lines"].append(log_line_to_dict(line, ' - '))
	except:

		log_dict["error"] = "can't read file"
	
	finally:

		return log_dict

def kill_process(pid, list_):
	"""
	Kills given process pid in list_.
	"""

	for process in list_:

		if process.pid == pid:

			process.terminate()

def kill_processes_list(list_):
	"""
	Terminates a list of processes.
	"""

	for process in list_:

		process.terminate()