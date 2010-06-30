# -*- coding: utf-8  -*-
import sys
import time  # throttling
import copy                   # copying Message instances
import irclib                 # communicating with the IRC server

from BaseClass import BaseClass

class IRC( BaseClass ):
	"""
	Class responsible for interacting with an IRC server.
	"""
	
	###########################################################################
	##	Initialize
	###########################################################################
	###################
	##	Constructor
	##	Initialize client & properties, set configuration.
	###################
	def __init__( self,
		server,
		port,
		nick,
		user,
		password,
		ssl,
		chans = None,
		debug = False,
		default_quit_reason = '*poof*',
		default_reset_reason = 'reset',
		max_message_size = 420,
		callback_pubmsg = None,
		throttle_seconds = 1.6,
		logger = None
	):
		BaseClass.__init__( self, logger = logger )
		self.trace(overrides = {'password':'<<hidden>>'})

		# data
		self.address = server
		self.port    = port
		self.nick    = nick
		self.user    = user
		self.password= password
		self.ssl = ssl
		self.chans   = chans
		self.callback_pubmsg = callback_pubmsg

		# configuration
		irclib.DEBUG              = debug
		self.default_quit_reason  = default_quit_reason
		self.default_reset_reason = default_reset_reason
		self.max_message_size     = max_message_size
		self.throttle             = throttle_seconds

		# throttled message queuing
		self.queue     = []          # list of messages to send
		self.next_send = time.time() # minimum epoch time when next message can be sent
		self.last_size = 0           # size of last message sent (used to increase wait time for long messages)

		# IRC backend
		self.irc = irclib.IRC()
		self.irc.add_global_handler( 'pubmsg', self.onPublicMessage )
		self.server = self.irc.server()
		self.server.add_global_handler( 'welcome', self.onConnect )
		self.server.add_global_handler( 'disconnect', self.onDisonnect )


	###################
	## begin processing input from server
	###################
	def processForever( self ):
		self.trace()
		self.irc.process_forever()

	def processOnce( self ):
		self.trace()
		self.irc.process_once()


	###########################################################################
	##	IRC message class
	###########################################################################
	class Message( object ):
		###################
		##	Constructor
		###################
		def __init__( self, conn = None, event = None ):
			if conn and event:
				self.conn  = conn
				self.event = event
				self.channel = event.target()
				self.text  = event.arguments()[0]
				self.mask  = event.source()
				self.nick  = None
				self.ident = None
				self.host  = None

				# parse nick/ident/host
				(self.nick, self.host)  = self.mask.split( '@', 2 )
				(self.nick, self.ident) = self.nick.split( '!' )

		###################
		##	Return copy of self
		###################
		def copy( self ):
			_copy = IRC.Message()
			for ( key, item ) in self.__dict__.items():
				_copy.__dict__[key] = copy.copy( item )
			return _copy


	###########################################################################
	##	Generic IRC functions
	###########################################################################
	###################
	##	Connect to network, join channels
	###################
	def connect( self ):
		self.trace()
		if self.ssl == True:
			self.server.connect( self.address, self.port, self.nick, self.password, self.user, ssl=True )
		else:
			self.server.connect( self.address, self.port, self.nick, self.password, self.user )

	def onConnect( self, conn, event ):
		self.trace()
		for chan in self.chans:
			self.server.join( chan )


	###################
	##	Disconnect, exit
	###################
	def disconnect( self, msg = None ):
		self.trace()
		self.server.remove_global_handler( 'disconnect', self.onDisonnect )
		self.server.add_global_handler( 'disconnect', self.onChosenDisconnect )
		self.server.disconnect( msg if msg else self.default_quit_reason )

	def onChosenDisconnect( self, conn, event ):
		self.trace()
		sys.exit( 0 )


	###################
	##	Reset web cookies, IRC connection
	##	onDisonnect also handles auto-reconnection.
	###################
	def reset( self, msg = None ):
		self.trace()
		self.server.disconnect( msg if msg else self.default_reset_reason )

	def onDisonnect( self, conn, event ):
		self.trace()
		self.connect()


	###################
	##	[{Private] send a message to the IRC server, transparently throttling.
	###################
	def _sendMessage( self, target, message ):
		self.trace()

		# split message along max size & queue
		lines = [message[i:i+self.max_message_size] for i in range( 0, len(message), self.max_message_size )]
		for line in lines:
			self.traceMessage('	>> ' + line)
			self.queue.append( [target, line] )

		# reset last size if past delay
		if time.time() >= self.next_send:
			self.last_size = 0

		# send messages in queue
		for i in range( len(self.queue) ):
			# get message data
			(target, line) = self.queue.pop( 0 )

			# delay post if over the limit
			if time.time() < self.next_send:
				# wait until throttle expires
				time.sleep( self.next_send - time.time() )

				# extend wait if last message was particularly large
				if self.last_size > (0.5 * self.max_message_size):
					time.sleep( self.throttle )
				if self.last_size > (0.9 * self.max_message_size):
					time.sleep( self.throttle )

			# send message
			self.server.privmsg( target, self.Encode(line) )
			self.last_size = len(line)
			self.next_send = time.time() + self.throttle


	###################
	##	Send a message to an IRC channel
	###################
	def sendMessage( self, chan, nick, msg ):
		self.trace()

		if( nick ):
			msg = u'%s: %s' % ( self.Decode(nick), self.Decode(msg) )

		self._sendMessage(
			target  = chan,
			message = msg
		)


	###################
	##	Send a message to an IRC user
	###################
	def sendPrivateMessage( self, nick, msg ):
		self.trace()
		self._sendMessage(
			target  = nick,
			message = msg
		)


	###############
	# Handle public message
	###############
	def onPublicMessage( self, conn, event ):
		#self.trace( )
		if self.callback_pubmsg:
			self.callback_pubmsg( self.Message(conn, event) )


	###########################################################################
	##	Getters
	###########################################################################
	###############
	# List of channels
	###############
	def getChannels( self ):
		self.trace()
		return self.chans