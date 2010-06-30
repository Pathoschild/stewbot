import time
from ILogger import ILogger
import Formatting

class LogFile(ILogger):
	"""
	An implementation of ILogger that sends messages to a file.
	"""
	
	def __init__(self, file_path ):
		"""
		Initialize the file logger.
		"""
		self.file = open( file_path, 'a' )
	
	
	def GetLocationString(self):
		"""
		Get a brief human-readable description of the location of the log,
		such as "console" or "file 'bot.log'".
		
		@return str: brief description of location.
		"""
		return "file at <%s>" % self.file.name
	
	
	def Log(self, message):
		"""
		Log a message to the console.
		
		@param message: arbitrary message to log.
		@return None
		"""
		self.file.write("[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), Formatting.Encode(message)))
		

	def __del__(self):
		"""
		Release all resources when the logger is being deleted.
		"""
		self.file.close()