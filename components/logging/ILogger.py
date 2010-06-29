class ILogger(object):
	"""
	Interface for a class responsible for logging messages to an arbitrary medium.
	"""
	
	def Log(self, message):
		"""
		Log an arbitrary message.
		"""
		pass