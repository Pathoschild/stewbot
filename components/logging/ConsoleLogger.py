import time
from ILogger import ILogger

class ConsoleLogger(ILogger):
	"""
	An implementation of ILogger that sends messages to the current console.
	"""
	
	def Log(self, message):
		"""
		Log a message to the console.
		"""
		print "[" + time.strftime("%Y-%m-%d %H:%M:%S") + "] " + str(message)