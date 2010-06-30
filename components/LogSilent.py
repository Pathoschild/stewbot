from ILogger import ILogger

class LogSilent(ILogger):
	"""
	An implementation of ILogger that discards all messages.
	"""
	def GetLocationString(self):
		"""
		Get a brief human-readable description of the location of the log,
		such as "console" or "file 'bot.log'".
		
		@return str: brief description of location.
		"""
		return "nowhere"
	
	
	def Log(self, message):
		"""
		Do nothing.
		
		@param message: arbitrary message to do nothing with.
		@return None
		"""
		pass