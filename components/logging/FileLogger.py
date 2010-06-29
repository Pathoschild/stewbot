import time
from ILogger import ILogger

class FileLogger(ILogger):
	"""
	An implementation of ILogger that sends messages to a file.
	"""
	
	def __init__(self, file_path ):
		"""
		Initialize the file logger.
		"""
		self.file = open( file_path, 'a' )
	
	
	def Log(self, message):
		"""
		Log a message to the console.
		"""
		self.file.write("[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), str(message)))
		

	def __del__(self):
		"""
		Release all resources when the logger is being deleted.
		"""
		self.file.close()