import re
import sys
import inspect
import traceback
from stewbot.interfaces.ILogger import ILogger
from stewbot.components.Interface import Interface
from stewbot.components.LogSilent import LogSilent
from stewbot.components.modules.Formatting import Formatting

class BaseClass( object ):
	"""
	Provides common methods for encoding & decoding text, logging messages,
	handling errors, and manipulating strings.
	"""

	class Error( Exception ):
		"""
		The base error class.
		"""

	class LoginTokenRequestedError( Error ):
		"""
		Error which indicates that a login token must be sent back to complete login (MediaWiki 1.15.3+); the exception
		message is the token.
		"""

	###########################################################################
	##	Constructor
	###########################################################################
	def __init__( self, logger ):
		"""
			Initialize the base class and validate the logger component.

			@param logger: the ILogger object tasked with dispatching debug messages.

			@type logger: ILogger
		"""
		self.logger = logger
		self.re_address = re.compile( '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/(?:1[6-9]|2[0-9]|3[0-2]))?$' )

		Interface.Assert(self.logger, ILogger)


	###########################################################################
	##	String manipulation
	###########################################################################
	def Decode(self, input):
		"""
			Decode the arbitrary input string into a standard Unicode string.

			@param input: string to parse.
			@return unicode: decoded string.
		"""
		return Formatting.Decode(input)


	def Encode(self, obj):
		"""
		Encode the arbitrary input string into a raw UTF-8 bytestring. This is
		necessary when passing text to a third-party module, because most modules
		are incapable of processing decoded text.

		@param obj: string to parse.
		@return str: encoded string.
		"""
		return Formatting.Encode(obj)


	def UrlEncode( self, obj ):
		"""
		Convert the dict into an escaped HTTP query string, without the leading
		? character.

		@param obj: dict to parse.
		@return str: encoded URL query string.
		"""
		return Formatting.UrlEncode(obj)


	def capitalizeFirstLetter( self, text ):
		"""
		Capitalize the first character in the string.

		@param text: string to modify.
		@return str: modified string.
		"""
		self.trace()

		if text[0].isupper():
			return text

		else:
			text = list(text)
			text[0] = text[0].upper()
			text = ''.join(text)
			return text


	def isAddress( self, text ):
		"""
		Indicate whether a string represents a valid IP address.

		@param text: string to check.
		@return bool: whether the string is a valid IP address.
		"""
		self.trace()
		return self.re_address.match( text )


	def isInt( self, text ):
		"""
		Indicate whether a string represents a valid integer.

		@param text: string to check.
		@return bool: whether the string is a valid integer.
		"""
		self.trace()
		try:
			int(text)
			return True
		except TypeError:
			return False
		except ValueError:
			return False


	###########################################################################
	##	Profiling & error-handling
	###########################################################################
	def trace( self, overrides=None ):
		"""
		Send debug information about the containing function call to the logger.

		@keyword overrides: a dict of parameter names and values. When printing
			the parent function call's parameters, this is checked for overrides
			to display instead of the actual value.
		@return None
		"""
		if not isinstance(self.logger, LogSilent): # avoid pointless computing
			try:
				# get frame
				frame  = inspect.stack()[1][0]

				# get names
				module = inspect.getmodule( frame.f_code )
				if module is not None:
					module = module.__name__
				else:
					module = ""
				function = frame.f_code.co_name

				# get arguments
				args = inspect.getargvalues( frame )
				if overrides:
					for k in overrides.keys():
						args[3][k] = overrides[k]
				if args[0][0] == 'self':
					args[0].pop(0)
					del args[3]['self']

				arg_string = inspect.formatargvalues(
					args        = args[0],
					varargs     = args[1],
					varkw       = args[2],
					locals      = args[3],
					formatvalue = lambda v: u'=%s' % self._FormatArg(self.Decode(v))
				)

				# trace
				self.logger.Log('%s::%s%s' % (module, function, arg_string))
			finally:
				del frame


	def traceMessage( self, msg ):
		"""
		Send an arbitrary message to the logger.

		@param msg: string message to send to the logger.
		@return None
		"""
		self.logger.Log(msg)


	def HandleException(self):
		"""
		Fetch details about the last exception raised from the system, dispatch
		them to the log, and return a simplified summary string suitable for
		display in the user interface.

		@return (str, str) tuple: simplified summary of exception & detailed
			stack trace.
		"""
		self.trace()

		# get data
		(type, value, tb) = sys.exc_info()
		tb = traceback.format_exc()

		# dispatch message to exception logger
		logExc = '\n'
		logExc += '##########################################################\n'
		logExc += '### AN EXCEPTION OCCURRED:\n'
		logExc += '###\n'
		logExc += '### %s\n' % '\n### '.join( tb.splitlines() )
		logExc += '###'
		logExc += '##########################################################'
		self.logger.Log(logExc)

		# return summary for UI display
		tb_last = traceback.format_exc().splitlines()
		tb_last = tb_last[len(tb_last)-3] # get 3rd line from bottom (last detail before error, code)
		return (
			"%s: %s. %s" % (type.__name__, str(value), str(tb_last)),
			logExc
		)

	###########################################################################
	## Private methods
	###########################################################################
	def _FormatArg( self, value ):
		"""
		Format an arbitrary argument for trace output.

		@param value: an arbitrary object to format for output.
		"""
		if isinstance(value, BaseClass):
			return u'<%s>' % inspect.getmodule(value).__name__
		elif inspect.ismethod(value):
			return u'{%s::%s}' % (inspect.getmodule(value).__name__, value.__name__)
		elif inspect.isfunction(value):
			return u'{%s}' % value.__name__
		else:
			return value
