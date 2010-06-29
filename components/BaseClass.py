#######################################################
##	BaseClass
##	Contains common class methods and properties.
##
##	Public properties:
##		Error()
##			Instance of Exception raised on error.
##
##	Public methods:
##		verbose( function, locals )
##			If VERBOSE, print function call to console.
##		parse( obj<str> )
##			convert any string object to a UTF-8 Unicode string.
##		isAddress( text<str> )<bool>
##			returns boolean: text is an IP address?
#######################################################
import re     # re, match
import sys
import urllib # urlencode
import inspect
import traceback
import chardet
from components.Interface import Interface
from components.logging.ILogger import ILogger
from components.logging.SilentLogger import SilentLogger

class BaseClass( object ):
	###########################################################################
	##	Constructor
	##	Initialize properties.
	###########################################################################
	def __init__( self, logger ):
		self.logger = logger
		self.re_address = re.compile( '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/(?:1[6-9]|2[0-9]|3[0-2]))?$' )
		
		Interface.Assert(logger, ILogger)


	###########################################################################
	##	Profiling & error-handling
	###########################################################################
	###################
	##	Error class
	##	Raised with error messages
	###################
	class Error( Exception ):
		"""Base error class"""
	class LoginTokenRequestedError( Error ):
		"""
		Indicates a login token must be sent back to complete login (MediaWiki 1.15.3+);
		the exception message is the token.
		"""

	###################
	##	Format argument
	##	Given an arbitrary argument, format it for trace output
	###################
	def formatArg( self, value ):
		# determine value
		if isinstance( value, BaseClass ):
			return u'<%s>' % inspect.getmodule( value ).__name__
		elif inspect.ismethod( value ):
			return u'{%s::%s}' % (inspect.getmodule( value ).__name__, value.__name__)
		elif inspect.isfunction( value ):
			return u'{%s}' % value.__name__
		else:
			return value


	###################
	##	Trace
	##	If VERBOSE, print function call to console.
	###################
	def trace( self, overrides=None ):
		if not isinstance(self.logger, SilentLogger): # avoid pointless computing
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
					formatvalue = lambda v: u'=%s' % self.formatArg(self.parse(v, suppress_trace = True))
				)

				# trace
				self.logger.Log('%s::%s%s' % (module, function, arg_string))
			finally:
				del frame


	###################
	##	TraceMessage
	##	If VERBOSE, print message to console.
	###################
	def traceMessage( self, msg ):
		self.logger.Log(msg)


	###################
	##	Print a formatted traceback to the console for the last raised exception,
	##	and return summary suitable for display on IRC.
	###################
	def handleException( self ):
		return self.formatException()
	def formatException( self ):
		self.trace()

		# get data
		(type, value, tb) = sys.exc_info()
		tb = traceback.format_exc()

		# extract details from traceback for IRC
		tb_last = traceback.format_exc().splitlines()
		tb_last = tb_last[len(tb_last)-3] # get 3rd line from bottom (last detail before error, code)

		self.logger.Log(self.formatFullException())
		return "%s: %s. %s" % (type.__name__, str(value), str(tb_last))

	def formatFullException( self ):
		(type, value, tb) = sys.exc_info()
		tb = traceback.format_exc()

		exc = '\n'
		exc += '##########################################################\n'
		exc += '### AN EXCEPTION OCCURRED:\n'
		exc += '###\n'
		exc += '### %s\n' % '\n### '.join( tb.splitlines() )
	 	exc += '###'
		exc += '##########################################################'
		exc +=''
		return exc


	###########################################################################
	##	String manipulation
	###########################################################################
	###################
	##	Parse
	##	Force a string to utf-8 Unicode
	###################
	def parse( self, obj, encodings = ['utf-8', 'ISO-8859-1', 'CP1252', 'latin1'], suppress_text = True, suppress_trace = True ):
		if not suppress_trace:
			self.trace() if not suppress_text else self.trace( overrides = {'obj':'<<hidden>>'} )

		# if self.Error, convert to string first
		if isinstance( obj, self.Error ):
			obj = obj.args[0]

		########
		# Unicode?
		########
		if isinstance( obj, unicode ):
			return obj

		########
		# String?
		########
		elif isinstance( obj, str ):
			########
			# Common encoding?
			########
			for encoding in encodings:
				try:
					string = obj.decode( encoding )
					return string
				except UnicodeDecodeError, e:
					continue

			########
			# Try encoding detection algorithm
			########
			self.logger.Log('	>> unable to resolve text encoding, trying heuristic detection... ')
			try:
				detector = chardet.detect( obj )
				self.logger.Log('		%s (%s confidence)... ' % ( detector['encoding'], detector['confidence'] ))
				string = obj.decode( detector['encoding'] )
				self.logger.Log('		ok!')
				return string
			except UnicodeDecodeError:
				self.logger.Log('		failed!')

			########
			# Everything failed, try pretending nothing happened
			########
			# pretend it's ok?
			self.logger.Log('	>> try pretending it\'s ok?')
			return obj

		########
		# Numeric?
		########
		elif isinstance( obj, int ):
			return str( obj )

		########
		# Anything else
		########
		else:
			return obj


	###################
	##	Unparse
	##	Decodes a UTF-8 Unicode string into bytes
	###################
	def unparse( self, obj, suppress_text = True, suppress_trace = True ):
		if not suppress_trace:
			self.trace() if not suppress_text else self.trace( overrides = {'obj':'<<hidden>>'} )

		if isinstance( obj, unicode ):
			return obj.encode('utf-8')
		return obj

	###################
	##	urlEncode
	##	Converts hash to URL-encoded string
	###################
	def urlEncode( self, obj, suppress_trace = True ):
		self.trace() if not suppress_trace else self.trace( {'obj':'<<hidden>>'} )

		_obj = {}
		for k in obj.keys():
			_obj[self.unparse(k)] = self.unparse( obj[k] )
		return urllib.urlencode( _obj )

		#return urllib.urlencode( obj )
		# flatten
		#str = ''
		#for k in obj.keys():
		#	v = "%s" % self.unparse(obj[k])
		#	k = "%s" % self.unparse(k)
		#	str += u"%s=%s&" % ( urllib.quote(k), urllib.quote(v) )
		#str = str.rstrip( '&' )
		#
		#return str


	###################
	## capitalize first letter
	###################
	def capitalizeFirstLetter( self, text ):
		self.trace()

		if text[0].isupper():
			return text

		else:
			text = list(text)
			text[0] = text[0].upper()
			text = ''.join(text)
			return text


	###################
	##	isAddress
	##	Boolean: string is IP address?
	###################
	def isAddress( self, text ):
		self.trace()
		return self.re_address.match( text )


	###################
	##	isInt
	##	Boolean: string is an integer?
	###################
	def isInt( self, text ):
		self.trace()
		try:
			int(text)
			return True
		except TypeError:
			return False
		except ValueError:
			return False


	###########################################################################
	##	Object manipulation
	###########################################################################
	###################
	##	hasIndex
	##	Boolean: object has the specified index?
	###################
	def hasIndex( self, obj, i ):
		self.trace()
		try:
			obj[i]
			return True
		except:
			return False
