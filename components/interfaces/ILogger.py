class ILogger(object):
	"""
	Represents a class responsible for logging messages to an arbitrary medium.
	"""
	
	def GetLocationString(self):
		"""
		Get a brief human-readable description of the location of the log,
		such as "console" or "file 'bot.log'".
		
		@return str: brief description of location.
		"""
		pass
		
	def Log(self, message):
		"""
		Log an arbitrary message.
		
		@param message: arbitrary message to log.
		@return None
		"""
		pass
