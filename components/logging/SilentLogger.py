from ILogger import ILogger

class SilentLogger(ILogger):
	"""
	An implementation of ILogger that discards all messages.
	"""
	
	def Log(self, message):
		"""
		Do nothing.
		"""
		pass