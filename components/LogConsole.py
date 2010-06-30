import time
from ILogger import ILogger
import Formatting

class LogConsole(ILogger):
	"""
	An implementation of ILogger that sends messages to the current console.
	"""
	def GetLocationString(self):
		"""
		Get a brief human-readable description of the location of the log,
		such as "console" or "file 'bot.log'".
		
		@return str: brief description of location.
		"""
		return "console"
	
	
	def Log(self, message):
		"""
		Log a message to the console.
		
		@param message: arbitrary message to log.
		@return None
		"""
		print "[" + time.strftime("%Y-%m-%d %H:%M:%S") + "] " + Formatting.Encode(message)