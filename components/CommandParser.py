# -*- coding: utf-8  -*-
#######################################################
##	CommandParser
##	Abstracts user access restriction and command parsing.
#######################################################
import re
import copy
from BaseClass import BaseClass

###################
## CommandParser class
###################
class CommandParser( BaseClass ):
	###########################################################################
	##	Constructor
	##	Populates internal hashes.
	###########################################################################
	def __init__( self,
		commands,                   # hash of levels and commands: {0:['foo',...], 1:[...]}
		users,                      # hash of levels and users: {1:['person',...], 2:[...]}
		logger,                     # an ILogger implementation to send log messages to
		callback = None,            # an instance; if not None, it will call:
		                            # - handle_<command> for valid commands;
		                            # - handle_None for valid command if handle_<command> not defined;
		                            # - handle_Error for errors;
		                            # - handle_Commit for commit command, with queued command as data.queued (else calls queued command's handler)
		                            # - handle_Queued if command queued for commit.
		banned = None,              # array of regexes to match against the hostmask, for ignored users
		command_prefix = '!~',      # characters to recognize as the start of a command at beginning of line
		command_delimiter = '<>',   # characters to recognize as delimiters between arguments
		handle_commit = True,       # handle !commit and !cancel?
		no_commit_commands = [],    # array of commands that cannot be !commit'd
		commit_req_user_level = 1,  # access level required to queue a command for !commit
		commit_imp_user_level = 2,   # access level required to !commit a queued command
	):
		BaseClass.__init__( self, logger = logger )
		self.trace()

		# constants
		self.ERROR         = 0
		self.IGNORED       = 1
		self.OKAY          = 2
		self.COMMIT        = 3

		self.USER_BANNED   = -9
		self.NOT_COMMAND   = -8
		self.BLANK_ARGS    = -7
		self.NO_COMMIT_ID_GIVEN = -6
		self.NO_SUCH_COMMIT_ID  = -5
		self.CANNOT_COMMIT = -4
		self.NOT_ALLOWED   = -3
		self.HANDLED       = -2
		self.MUST_COMMIT   = -1

		# flag associations and descriptions
		self.flags = {
			# summary flags
			self.ERROR:[None, 'ERROR', 'An error has occurred (see data.flag property)'],
			self.IGNORED:[None, 'IGNORED', 'The input was ignored (see data.flag property)'],

			# detail flags
			self.USER_BANNED:[self.IGNORED, 'USER_BANNED', 'You are banned from giving me commands'],
			self.NOT_COMMAND:[self.IGNORED, 'NOT_COMMAND', 'That is not recognized as a command'],
			self.BLANK_ARGS:[self.ERROR, 'BLANK_ARGS', 'Arguments cannot be blank'],
			self.NOT_ALLOWED:[self.ERROR, 'NOT_ALLOWED', 'No'],#'You have insufficient access to issue that command'],
			self.CANNOT_COMMIT:[self.ERROR, 'CANNOT_COMMIT', 'You have insufficient access to issue that command, and it cannot be committed'],
			self.NO_SUCH_COMMIT_ID:[self.ERROR, 'NO_SUCH_COMMIT_ID', 'No commit id'],
			self.NO_COMMIT_ID_GIVEN:[self.ERROR, 'NO_COMMIT_ID_GIVEN', 'No commit id specified'],
			self.MUST_COMMIT:[self.MUST_COMMIT, 'MUST_COMMIT', 'The command has been queued for !commit'],
			self.OKAY:[self.OKAY, 'OKAY', 'The command was parsed and validated, and awaits implementation']
		}

		# input
		self.command_groups    = commands
		self.callback          = callback
		self.user_groups       = users
		self.banned_users      = banned
		self.handle_commit     = handle_commit
		self.no_commit         = no_commit_commands
		self.cmd_prefix        = command_prefix
		self.cmd_delim         = command_delimiter
		self.commit_req_level  = commit_req_user_level
		self.commit_imp_level  = commit_imp_user_level

		# tracking variables
		self.commit_id    = -1
		self.commit_queue = {}

		# handle commit & cancel
		if self.handle_commit:
			# add level to command
			if self.commit_imp_level not in self.command_groups:
				self.command_groups[self.commit_imp_level] = []

			# add to lists
			for cmd in ('commit', 'cancel'):
				self.command_groups[self.commit_imp_level].append( cmd )
				self.no_commit.append( cmd )

		# lookup hashes
		self.command_hash = {}
		self.user_hash    = {}
		for group in commands:
			for command in self.command_groups[group]:
				self.command_hash[command] = group or 0
		for group in self.user_groups:
			for user in self.user_groups[group]:
				if user in self.user_hash:
					raise ValueError( "Cannot parse user access list, user '%s' is assigned multiple access levels (%s, %s)" % (user, self.user_hash[user], group) )
				self.user_hash[user] = group

		# build regexes
		self.re_possible_cmd = re.compile( '^[%s]\S' % self.cmd_prefix )
		self.re_has_args     = re.compile( '^.[^%s\s]+(\s*[%s]|\s+[^%s])' % (self.cmd_delim, self.cmd_delim, self.cmd_delim) )
		self.re_parse_cmd    = re.compile( '^.([^%s\s]+)(?:\s*[%s]\s*|\s+|$)(.*)$' % (self.cmd_delim, self.cmd_delim) )
		self.re_split_args   = re.compile( '\s*[%s]\s*' % self.cmd_delim )

		if banned and len(banned):
			self.re_banned_mask = re.compile( '|'.join(self.banned_users) )
		else:
			self.re_banned_mask = None


	###########################################################################
	##	Public interface
	###########################################################################
	###################
	## Handle line
	###################
	def handle( self, data ):
		self.trace()

		##########
		## Ignore non-commands and banned users
		##########
		if not self.re_possible_cmd.match( data.text ):
			return self._callback( data, self.NOT_COMMAND )
		if self.re_banned_mask and self.re_banned_mask.search(data.mask):
			return self._callback( data, self.USER_BANNED )

		##########
		## Parse & validate
		##########
		self.data = copy.copy( data )
		self.data = self.resolve( self.data )

		# command does not exist
		if self.data.command not in self.command_hash:
			return self._callback( self.data, self.NOT_COMMAND )

		# blank args
		for arg in self.data.args:
			if not arg:
				return self._callback( self.data, self.BLANK_ARGS)

		##########
		## Handle security
		##########
		# insufficient access
		if self.data.user_level < self.data.command_level:
			# can commit?
			if self.handle_commit and self.data.user_level >= self.commit_req_level:
				if self.data.command in self.no_commit:
					return self._callback( self.data, self.CANNOT_COMMIT )
				else:
					self.queue( self.data )
					return self._callback( self.data, self.MUST_COMMIT )
				return self.data

			# ...else fail
			else:
				return self._callback( self.data, self.NOT_ALLOWED )


		##########
		## Callback or return
		##########
		return self._callback( self.data, self.OKAY )


	###################
	## Parse line into command (without validation or handling)
	###################
	def resolve( self, data ):
		self.trace()
		data.text       = self.Decode(data.text)
		data.commit_id  = None
		data.error_text = None

		# extract command and args
		groups = self.re_parse_cmd.search( data.text )
		data.command = groups.group( 1 ).lower()
		if self.re_has_args.search( data.text ):
			data.args = self.re_split_args.split( groups.group(2) )
		else:
			data.args = []

		# extract access levels
		data.user_level = self.user_hash[data.host] if data.host in self.user_hash else 0
		if data.command in self.command_hash:
			data.command_level = self.command_hash[data.command]
		else:
			data.command_level = None

		# return
		return data


	###################
	## Return text representation of given flag
	###################
	def name(self, flag):
		self.trace()
		return self.flags[flag][1]

	def explain(self, data):
		self.trace()

		# handle data object
		try:
			if data.flag_text:
				return data.flag_text

			elif data.flag == self.NO_SUCH_COMMIT_ID:
				return "%s %s" % (self.flags[data.flag][2], data.commit_id)
			return self.flags[data.flag][2]

		# handle constant
		except KeyError:
			return self.flags[data][2]


	###########################################################################
	##	Command queuing
	###########################################################################
	###################
	## Fetch list of queued IDs
	###################
	def listQueued( self ):
		self.trace()
		return self.commit_queue.keys()


	###################
	## Queue command for commit
	###################
	def queue( self, data ):
		self.trace()

		self.commit_id += 1
		data.commit_id = self.commit_id
		self.commit_queue[self.commit_id] = copy.copy( data )

		return data.commit_id


	###################
	## Peek at command in queue
	###################
	def peekQueue( self, id ):
		self.trace()
		return copy.copy( self.commit_queue[id] )


	###################
	## Filter list of IDs into (queued, not_queued)
	###################
	def filterByQueued( self, ids ):
		self.trace()

		queued     = []
		not_queued = []

		for id in ids:
			if id in self.commit_queue:
				queued.append( id )
			else:
				not_queued.append( id )

		return (queued, not_queued)


	###################
	## Returns (queued, not_queued) given "all", id, or id:id range
	###################
	def parseQueueId( self, ids ):
		self.trace()

		ids = ids.lower()
		if ids == 'all':
			return (self.listQueued(), [])

		elif re.search( '^\d+:\d+$', ids ):
			(min, max) = ids.split( ':', 1 )
			ids = range( int(min), int(max) + 1 )
			return self.filterByQueued( ids )

		elif self.isInt( ids ):
			return self.filterByQueued( [int(ids)] )

		else:
			return ([], ids)


	###################
	## Unqueue command for commit
	###################
	def unqueue( self, id ):
		self.trace()

		data = self.commit_queue[id]
		del self.commit_queue[id]

		return data


	###################
	## Commit command
	###################
	def commit( self, id ):
		self.trace()
		data = self.unqueue( id )
		return self._callback( data, self.OKAY )



	###################
	## Cancel command
	###################
	def cancel( self, id ):
		self.trace()
		return self.unqueue( id )


	###########################################################################
	##	Private methods
	###########################################################################
	###################
	## Set data settings
	###################
	def _setFlags( self, data, flag, flag_text = None ):
		self.trace()
		data.flag       = flag
		data.flag_group = self.flags[flag][0]
		data.flag_text  = flag_text
		return data


	###################
	## Fire callback and return data
	###################
	def _callback( self, data, flag = None, flag_text = None ):
		if flag or flag_text:
			self._setFlags( data, flag, flag_text )


		if self.callback:
			if data.flag in (self.IGNORED, self.NOT_COMMAND, self.USER_BANNED):
				return data

			## determine method name
			method_name = ""
			if data.flag_group == self.OKAY:
				method_name = 'handle_%s' % data.command
			elif data.flag_group == self.ERROR:
				method_name = 'handle_Error'
			elif data.flag_group == self.MUST_COMMIT:
				method_name = 'handle_Queued'
			elif data.flag_group == self.COMMIT:
				method_name = 'handle_Commit'
			else:
				raise ValueError( "Unrecognized flag group '%s'" % data.flag_group )

			## call method
			method = getattr( self.callback, method_name )
			if method:
				method( data )
				return data

			## if not found, call default handler
			method = getattr( self.callback, 'handle_None' )
			if method:
				method( data )
				return data

			## if still not found, raise exception
			raise ValueError( "Callback object has no method '%s', and no method 'handle_None' to delegate to" % method_name )
