#######################################################
##	Browser
##	Abstracts querying and scraping web pages, and parsing APIs.
#######################################################
import sys
sys.path.append( '../' )
sys.path.append( './modules' )

from BeautifulSoup import BeautifulSoup as htmldom
import mechanize
import re
import simplejson
import xml.dom.minidom as xmldom

from BaseClass import BaseClass

###################
##	Browser class
###################
class Browser( BaseClass ):
	###########################################################################
	##	Constructor
	##	Initialize class properties & browser backend
	###########################################################################
	def __init__( self, username, password, user_agent, obey_robot_rules = False, max_api_items = 200, verbose = True ):
		BaseClass.__init__( self, verbose = verbose )
		self.trace()

		# configuration
		self.username      = username
		self.password      = password
		self.max_api_items = max_api_items

		# browser
		self.browser = mechanize.Browser(factory=mechanize.RobustFactory())
		self.browser.addheaders = [('User-agent', user_agent)]
		self.browser.set_handle_robots( obey_robot_rules )

		# variables
		self.path_article = None
		self.path_index = None
		self.path_api = None
		self.url_base = None
		self.url_article = None
		self.url_index = None
		self.url_api = None

		self.def_path_article = None
		self.def_path_index = None
		self.def_path_api = None
		self.def_url_base = None
		self.def_url_article = None
		self.def_url_index = None
		self.def_url_api = None

		# tracking
		self.sessions = {}   # data for each session: { base_url:{logged_in:NAME, tokens:{edit:..., protect:..., ...}} }
		self.response = None # response, created by load()
		self.last_url = None # last URL loaded, dumped on exception
		self.text     = None # text of last page fetched
		self.parsed   = None # result of parsing text (if asked to), either data structure or parser


	###########################################################################
	##	Session & URL management
	###########################################################################
	###################
	##	Bot is logged in?
	###################
	def loggedIn( self, force_check = False ):
		self.trace()

		# force check
		if force_check:
			self.queryApi({
				'action':'query',
				'meta':'userinfo'
			})
			data = self.parsed.getElementsByTagName('userinfo')[0].getAttribute('name')
			logged_in = not self.isAddress( data )

			# update internal data
			self.sessions[self.url_base] = {
				'base_url':self.url_base,
				'logged_in':data if logged_in else False,
				'tokens':self.sessions[self.url_base]['tokens'] if logged_in else {}
			}

		# return current data
		if self.sessions[self.url_base]['logged_in']:
			return u'%s@%s' % (self.sessions[self.url_base]['logged_in'], self.sessions[self.url_base]['base_url'])
		else:
			return self.sessions[self.url_base]['logged_in']


	###################
	##	Create session
	###################
	def storeSession( self, base_url, username ):
		self.trace()

		self.sessions[base_url] = {
			'logged_in':username,
			'base_url':base_url,
			'tokens':{}
		}


	###################
	##	store token from session
	###################
	def storeSessionToken( self, type, token ):
		self.trace()
		self.sessions[self.url_base]['tokens'][type] = token


	###################
	##	Read token from session
	###################
	def readSessionToken( self, type ):
		self.trace()
		if type in self.sessions[self.url_base]['tokens'].keys():
			return self.sessions[self.url_base]['tokens'][type]
		else:
			return None


	###################
	##	Destroy session
	###################
	def destroySession( self, base_url ):
		self.trace()
		self.sessions[base_url]['logged_in'] = False
		self.sessions[base_url]['tokens'] = {}


	###################
	##	Set base URL for navigation (format: http://meta.wikimedia.org)
	###################
	def setBaseUrl( self, base_url, index_path = '/w/index.php', api_path = '/w/api.php', article_path = '/wiki/', set_default = False ):
		self.trace()

		self.path_article = article_path
		self.path_index   = index_path
		self.path_api     = api_path

		self.url_base    = base_url
		self.url_article = base_url + article_path
		self.url_index   = base_url + index_path
		self.url_api     = base_url + api_path

		if set_default:
			self.def_path_index   = index_path
			self.def_path_api     = api_path
			self.def_path_article = article_path

			self.def_url_base    = self.url_base
			self.def_url_article = self.url_article
			self.def_url_index   = self.url_index
			self.def_url_api     = self.url_api

		if self.url_base not in self.sessions:
			self.sessions[self.url_base] = {
				'logged_in':False
			}


	###################
	##	Reset URL to default
	###################
	def resetBaseUrl( self ):
		self.trace()

		if not self.def_url_base:
			raise self.Error, u'cannot resetBaseUrl() before defining default URLs'

		self.path_index   = self.def_path_index
		self.path_api     = self.def_path_api
		self.path_article = self.def_path_article

		self.url_base    = self.def_url_base
		self.url_article = self.def_url_article
		self.url_index   = self.def_url_index
		self.url_api     = self.def_url_api


	###################
	##	Clear & reset all data
	###################
	def reset( self ):
		self.trace()
		self.resetBaseUrl()

		for url in self.sessions:
			self.destroySession( url )


	###########################################################################
	##	Page fetching
	###########################################################################
	###################
	##	Open page at the current URL, set response
	##	required: setBaseUrl()
	###################
	def load( self, url = None, title = None, parameters = None, GET = False, visit = False, parse_as = None, unicodify = True, censor_url = False, catch_errors = True ):
		self.trace()

		# get URL & query string
		if not url:
			if not title:
				raise self.Error, 'Browser::load called with no URL or page title to load'
			url = self.url_base + self.path_article + title

		if parameters:
			parameters = self.urlEncode( parameters )

		# force GET mode?
		if GET and parameters:
			if url.find( '?' ) != -1:
				url = '%s%s' % (url, '&%s' % parameters)
			else:
				url = '%s%s' % (url, '?%s' % parameters)
			parameters = None
			self.last_url = url
		else:
			self.last_url = u'%s  <<  %s' % (url, parameters)

		if censor_url:
			self.last_url = '<<hidden>>'
		if self.verbose:
			print self.last_url

		# load page
		if visit:
			self.response = self.browser.open( url, parameters )
			
			# bugfix -- mechanize confused by <br/>
			self.response.set_data(self.response.get_data().replace("<br/>", "<br />"))
			self.browser.set_response(self.response)
		else:
			self.response = self.browser.open_novisit( url, parameters )

		# fetch page text
		self.text = self.response.read()
		if unicodify:
			self.text = self.parse( self.text )

		# parse page text
		if not parse_as:
			self.parsed = None
			return

		parse_as = parse_as.lower()
		if parse_as == 'xml':
			self.parsed = xmldom.parseString( self.unparse(self.text) )
			if catch_errors:
				self.handleApiErrors()

		elif parse_as == 'html':
			self.parsed = htmldom( self.unparse(self.text) )
			if catch_errors:
				self.handleHtmlErrors()

		elif parse_as == 'json':
			self.parsed = simplejson.loads( self.unparse(self.text) )
		else:
			raise self.Error, 'Browser::load cannot parse text as "%s", unrecognized format' % parse_as


	###################
	##	Submit API query & handle response
	##	required: setBaseUrl()
	###################
	def queryApi( self, parameters, GET = False, censor_url = False ):
		self.trace( overrides = {'parameters':'<<hidden>>'} )

		# validate
		if not self.url_api:
			raise self.Error, 'cannot queryApi() before defining base URL'
		if not parameters:
			raise self.Error, 'cannot queryApi() with no parameters'


		# parse arguments
		if 'format' not in parameters:
			parameters['format'] = 'xml'
		self.query = parameters

		self.load(
			url        = self.url_base + self.path_api,
			parameters = parameters,
			GET        = GET,
			censor_url = censor_url,
			parse_as   = parameters['format']
		)


	###################
	##	Submit current form
	##	required: setBaseUrl(), browser.select_form()
	###################
	def submit( self ):
		self.trace()

		self.response = self.browser.submit()
		self.text     = self.parse( self.response.read() )
		self.parsed   = htmldom( self.unparse(self.text) )
		self.handleHtmlErrors()


	###################
	##	Strip HTML markup from string
	###################
	def stripHtml( self, text, strip_newlines = True, suppress_text = False ):
		self.trace() if not suppress_text else self.trace({'text':'<<hidden>>'})

		text = re.sub( '<[^>\n]+>', '', text )
		text = re.sub( '<!--[\s\S]+?-->', '', text )
		if strip_newlines:
			text = re.sub( '\n', ' ', text )

		return text


	###################
	##	Given xmldom element, return text contents
	###################
	def readXmlElement( self, element ):
		self.trace()

		# get prebuilt string
		if( element.string ):
			return element.string

		# iterate over text nodes
		if( element.childNodes ):
			nodes = element.childNodes
			text = u''
			for node in nodes:
				if node.nodeType == node.TEXT_NODE:
					text = text + node.data
			return text

		# no text?
		else:
			return u''


	###########################################################################
	##	Error-handling
	###########################################################################
	###################
	##	Parse API response for errors, raise error if found
	###################
	def handleApiErrors( self ):
		self.trace()

		#######
		## Generic errors
		#######
		if self.parsed.getElementsByTagName( 'error' ):
			error = self.parsed.getElementsByTagName( 'error' )[0]
			if error.getAttribute('code'):
				print '%s: %s' % ( error.getAttribute('code'), error.getAttribute('info') )
				raise self.Error, '%s: %s' % ( error.getAttribute('code'), error.getAttribute('info') )
			else:
				raise self.Error, self.readXmlElement( error )

		if self.parsed.getElementsByTagName( 'query-continue' ):
			raise self.Error, 'Too many results, limit set to %s' % self.max_api_items

		#######
		## list = users
		#######
		if self.parsed.getElementsByTagName( 'users' ):
			item = self.parsed.getElementsByTagName( 'user' )[0]
			if item.getAttributeNode( 'invalid' ):
				raise self.Error, 'invalid user name'
			elif item.getAttributeNode( 'missing' ):
				raise self.Error, 'no such user'

		#######
		## Log events
		#######
		elif self.parsed.getElementsByTagName( 'logevents' ):
			pass # all errors generic

		#######
		## Login
		#######
		elif self.parsed.getElementsByTagName( 'login' ):
			error  = self.parsed.getElementsByTagName('login')[0]
			result = self.parse( error.getAttribute('result') )
			if result != 'Success':
				if result == 'NeedToken':
					raise self.LoginTokenRequestedError, self.parse( error.getAttribute('token') )
				else:
					raise self.Error, {
						'NoName':'NoName: You didn\'t set the lgname parameter',
						'Illegal':'Illegal: You provided an illegal username',
						'NoName':'NoName: You didn\'t set the lgname parameter',
						'Illegal':'Illegal: You provided an illegal username',
						'NotExists':'NotExists: The username you provided doesn\'t exist',
						'EmptyPass':'EmptyPass: You didn\'t set the lgpassword parameter or you left it empty',
						'WrongPass':'WrongPass: The password you provided is incorrect',
						'WrongToken':'WrongToken: The server asked to resubmit with a confirmation token, but refused the token it was given.',
						'WrongPluginPass':'WrongPluginPass: The password you provided is incorrect; an authentication plugin rather than MediaWiki itself rejected the password',
						'CreateBlocked':'CreateBlocked: The wiki tried to automatically create a new account for you, but your IP address has been blocked from account creation',
						'Throttled':'Throttled: You\'ve logged in too many times in a short time'
					}.get(result, 'unknown error: "%s"' % result)

		#######
		## prop=info
		#######
		elif 'prop' in self.query and self.query['prop'] == 'info':
			warnings = self.parsed.getElementsByTagName( 'warnings' )
			if len( warnings ):
				warning = warnings[0].getElementsByTagName( 'info' )[0]
				raise self.Error, '%s' % self.parse( self.readXmlElement(warning) )


	###################
	##	Parse errors from MediaWiki (or any other interface using an error/fail class), raise appropriate exceptions
	###################
	def handleHtmlErrors( self ):
		self.trace()

		error = self.parsed.find( lambda tag: tag.has_key('class') and tag.get('class') in ['fail', 'error'] )

		if error:
			error = self.stripHtml( u'%s' % error )
			raise self.Error, error


	###########################################################################
	##	MediaWiki API queries
	###########################################################################
	###################
	##	Log in
	##	required: setBaseUrl()
	###################
	def login( self, force_login = False ):
		self.trace()

		if force_login or not self.sessions[self.url_base]['logged_in']:
			# send initial login request
			try:
				self.queryApi({
					'action':'login',
					'lgname':self.username,
					'lgpassword':self.password
				}, censor_url = True)
			
			# In MediaWiki 1.15.3+, an extra step is needed
			except self.LoginTokenRequestedError, token:
				self.queryApi({
					'action':'login',
					'lgname':self.username,
					'lgpassword':self.password,
					'lgtoken':token
				}, censor_url = True)

			# store session
			self.storeSession( self.url_base, self.username )
			print '	logged in on %s' % self.url_base

			# clear page text
			self.text = '<<hidden>>'



	###################
	##	Log out
	###################
	def logout( self ):
		self.trace()

		self.queryApi({
			'format':'xml',
			'action':'logout'
		})
		self.destroySession( self.url_base )


	###################
	##	Fetch token
	##	required: setBaseUrl()
	###################
	def fetchToken( self, type, title = 'User:Pathoschild', user = None ):
		self.trace()
		self.login()

		# fetch userrights token
		token = ''
		if type == 'userrights':
			if not user:
				raise self.Error, "Cannot fetch userrights token without target username"

			self.queryApi({
				'action':'query',
				'list':'users',
				'ususers':self.username,
				'ustoken':'userrights'
			})
			item  = self.parsed.getElementsByTagName( 'user' )[0]
			token = self.parse( item.getAttribute('%stoken' % type) )

		# fetch any other token, with caching
		else:
			token = self.readSessionToken( type )
			if not token:
				self.queryApi({
					'action':'query',
					'prop':'info',
					'intoken':type,
					'titles':title
				})
				item  = self.parsed.getElementsByTagName( 'page' )[0]
				token = self.parse( item.getAttribute('%stoken' % type) )

		# extract token & store
		self.storeSessionToken( type, token )
		return token


	###################
	##	Get block status
	##	required: setBaseUrl()
	###################
	def getBlockStatus( self, user ):
		self.trace()
		
		# fetch data
		if self.isAddress( user ):
			self.queryApi({
				'action':'query',
				'list':'blocks',
				'bkip':user
			})			
		
		else:
			self.queryApi({
				'action':'query',
				'list':'blocks',
				'bkusers':user,
				'bklimit':1
			})
	
		# parse
		blocks = []
		for block in self.parsed.getElementsByTagName('block'):
			blocks.append({
				'id':block.getAttribute('id'),
				'user':block.getAttribute('user'),
				'by':block.getAttribute('by'),
				'timestamp':block.getAttribute('timestamp'),
				'expiry':block.getAttribute('expiry'),
				'reason':block.getAttribute('reason'),
				'nocreate':block.hasAttribute('nocreate'),
				'autoblock':block.hasAttribute('autoblock'),
				'noemail':block.hasAttribute('noemail'),
				'allowusertalk':block.hasAttribute('allowusertalk'),
				'hidden':block.hasAttribute('hidden')
			})		
		return blocks
		
	
	###################
	##	Get global blocks affecting an IP
	##	required: setBaseUrl() to metawiki
	###################
	def getGlobalBlocks( self, address ):
		self.trace()
		
		self.queryApi({
			'action':'query',
			'list':'globalblocks',
			'bgip':address
		})
		blocks = []
		for item in self.parsed.getElementsByTagName( 'block' ):
			blocks.append({
				'id':item.getAttribute('id'),
				'address':item.getAttribute('address'),
				'anononly':item.hasAttribute('anononly'),
				'by':item.getAttribute('by'),
				'bywiki':item.getAttribute('bywiki'),
				'timestamp':item.getAttribute('timestamp'),
				'expiry':item.getAttribute('expiry'),
				'reason':item.getAttribute('reason')
			})
		return blocks


	###################
	##	Block a user
	##	required: setBaseUrl()
	###################
	def block( self, user, expiry, reason, anononly = True, nocreate = True, noemail = True, hidename = False, allowusertalk = True, autoblock = True, reblockIfChanged = False, reblock = False ):
		self.trace()

		self.login()
		token = self.fetchToken( 'block' )

		# cancel if no need
		if reblockIfChanged:
			blocks = self.getBlockStatus( user )
			if len(blocks) > 0:
				block = blocks[0]
				if block['hidden'] == bool(hidename) and (block['expiry'] == expiry or (block['expiry'] == 'infinity' and expiry == 'never')):
					return False
				reblock = True

		# build query
		query = {
			'action':'block',
			'user':user,
			'expiry':expiry,
			'reason':reason,
			'token':token
		}
		if autoblock:
			query['autoblock'] = ''
		if anononly:
			query['anononly'] = ''
		if nocreate:
			query['nocreate'] = ''
		if noemail:
			query['noemail'] = ''
		if hidename:
			query['hidename'] = ''
		if allowusertalk:
			query['allowusertalk'] = ''
		if reblock:
			query['reblock'] = ''

		# submit
		self.queryApi( query )
		return True


	###################
	##	Unblock a user
	##	required: setBaseUrl()
	###################
	def unblock( self, user, reason ):
		self.trace()

		self.login()
		token = self.fetchToken( 'unblock' )

		# submit query
		self.queryApi({
			'action':'unblock',
			'user':user,
			'reason':reason,
			'token':token
		})


	###################
	##	Delete a page
	##	required: setBaseUrl()
	###################
	def delete( self, title, reason ):
		self.trace()

		self.login()
		self.queryApi({
			'action':'delete',
			'title':title,
			'reason':reason,
			'token':self.fetchToken( 'delete' )
		})
		return True


	###################
	##	Edit a page
	##	required: setBaseUrl()
	###################
	def edit( self, title, summary, text = '', section = None, bot = 0, minor = 0, recreate = 1, createonly = 0 ):
		self.trace( overrides={'text':'<<text removed>>'} )

		self.login()
		token = self.fetchToken('edit')

		# build query
		query = {
			'action':'edit',
			'title':title,
			'summary':summary,
			'text':text or '',
			'token':token
		}
		if section:
			query['section'] = section
		if bot:
			query['bot'] = int( bot )
		if minor:
			query['minor'] = int( minor )
		if recreate:
			query['recreate'] = int( recreate )
		if createonly:
			query['createonly'] = int( createonly )

		# submit
		self.queryApi( query, censor_url = True )

		# get revision ID
		edit = self.parsed.getElementsByTagName('edit')[0]
		return self.parse( edit.getAttribute('newrevid') )


	###################
	##	Count user's edits
	##	Returns a hash with total edits, new edits, top edits, and unreverted (new or top) edits.
	##	required: setBaseUrl()
	###################
	def countUserEdits( self, username ):
		self.trace()

		# submit query
		self.queryApi({
			'action':'query',
			'list':'usercontribs',
			'ucuser':username,
			'uclimit':self.max_api_items,
			'ucprops':'flags'
		},
		GET = True )

		# process data
		items = self.parsed.getElementsByTagName( 'item' )
		count = len( items )
		top   = 0
		new   = 0
		unreverted = 0
		for item in items:
			if item.getAttributeNode( 'top' ) or item.getAttributeNode( 'new' ):
				unreverted += 1
				if item.getAttributeNode( 'top' ):
					top += 1
				if item.getAttributeNode( 'new' ):
					new += 1

		# return data
		return {
			'edits':count,
			'new':new,
			'top':top,
			'unreverted':unreverted
		}


	###################
	##	Fetch user rights
	##	required: setBaseUrl()
	###################
	def getRights( self, username ):
		self.trace()

		# submit query
		self.queryApi({
			'action':'query',
			'list':'users',
			'usprop':'groups',
			'ususers':username
		},
		GET = True)

		# process
		groups = []
		items = self.parsed.getElementsByTagName( 'g' )
		for i in range( len(items) ):
			groups.append( self.parse(items[i].childNodes[0].nodeValue) )
		return groups


	###################
	##	Set user rights
	##	required: setBaseUrl()
	###################
	def setRights( self, username, groups, reason, allowUnchanged = False ):
		self.trace()
		self.login()

		# << NEW API CODE, WAITING FOR API USERRIGHTS TOKEN BUG >>
		## split into add/remove arrays
		#add    = []
		#remove = []
		#for group, value in groups.items():
		#	if( value ):
		#		add.append( group )
		#	else:
		#		remove.append( group )
		#
		## query API
		#self.queryApi({
		#	'action':'userrights',
		#	'user':username,
		#	'add':'|'.join( add ),
		#	'remove':'|'.join( remove ),
		#	'reason':reason,
		#	'token':self.fetchToken( 'userrights', user = username )
		#})

		# load form
		self.load( title = 'Special:UserRights', parameters = {'user':username}, GET = True, visit = True, parse_as = 'html' )
		self.browser.select_form( name = 'editGroup' )

		# apply changes
		changed = False
		for group, value in groups.items():
			try:
				control = self.browser.find_control( 'wpGroup-%s' % group ).items[0]
			except ValueError, e:
				raise self.Error, 'no local group called "%s"' % group
			if bool( control.selected ) != bool( value ):
				control.selected = int( value )
				changed = True
		if not changed:
			if allowUnchanged:
				return
			else:
				raise self.Error, 'no changes needed'

		# submit form
		self.browser.form['user-reason'] = reason
		self.submit()


	###########################################################################
	##	MediaWiki queries (screen-scraping)
	###########################################################################
	###################
	##	CentralAuth actions
	##	required: setBaseUrl() to metawiki
	###################
	def centralAuth( self, user, reason = '', lock = None, hide = None, oversightLocal = None, ignoreUnchanged = False ):
		self.trace()
		self.login()

		# validate
		if lock == None and hide == None and oversightLocal == None:
			raise self.Error, 'no lock or hide preferences specified'
		if lock not in (True, False, None) or hide not in (True, False, None) or oversightLocal not in (True, False, None):
			raise self.Error, 'hide and lock preferences must be one of (True, False, None)'
		
		# load form
		self.load( title = 'Special:CentralAuth', parameters = {'target':user}, GET = True, visit = True, parse_as = 'html' )
		try:
			self.browser.select_form( predicate = lambda form: 'wpMethod' in [item.name for item in form.controls] and form['wpMethod'] == 'set-status' )
		except mechanize.FormNotFoundError:
			raise self.Error, 'could not find set-status form from Special:CentralAuth'

		# parse input
		NAME_LOCK = 'wpStatusLocked'
		NAME_HIDE = 'wpStatusHidden'
		
		LOCK_IGNORE = None
		LOCK_NO     = "0"
		LOCK_YES    = "1"
		HIDE_NO     = ""
		HIDE_IGNORE = None
		HIDE_LISTS  = "lists"
		HIDE_SUPPRESSED = "suppressed"
		set_lock = LOCK_YES if lock else LOCK_NO if lock != None else LOCK_IGNORE
		set_hide = HIDE_SUPPRESSED if oversightLocal else HIDE_LISTS if hide else HIDE_NO if hide != None else HIDE_IGNORE

		# constants are invalid?
		if set_lock != LOCK_IGNORE and set_lock not in [k.name for k in self.browser.find_control(NAME_LOCK).items]:
			raise self.Error, 'invalid lock constant "%s", valid types are [%s]' % (set_lock, ', '.join([k.name for k in self.browser.find_control(NAME_LOCK).items]))
		if set_hide != HIDE_IGNORE and set_hide not in [k.name for k in self.browser.find_control(NAME_HIDE).items]:
			raise self.Error, 'invalid hide constant "%s", valid types are [%s]' % (set_hide, ', '.join([k.name for k in self.browser.find_control(NAME_HIDE).items]))
		
		# don't implicitly decrease hide level
		if set_hide == HIDE_LISTS and self.browser[NAME_HIDE][0] == HIDE_SUPPRESSED:
			set_hide = HIDE_SUPPRESSED
		
		# command is redundant?
		if set_lock in [LOCK_IGNORE, self.browser[NAME_LOCK][0]] and set_hide in [HIDE_IGNORE, self.browser[NAME_HIDE][0]]:
			if ignoreUnchanged:
				return False
			error = 'The global account "%s" is already ' % user
			if set_lock != None:
				error += 'locked' if set_lock == LOCK_YES else 'unlocked'
			if set_hide != None:
				if set_lock != None:
					error += ' and '
				error += 'hidden' if set_hide == HIDE_LISTS else 'globally oversighted' if set_hide == HIDE_SUPPRESSED else 'unhidden'
			raise self.Error, error
				
		# modify form
		if set_lock != LOCK_IGNORE:
			control = self.browser.find_control(NAME_LOCK).get(set_lock).selected = True
		if set_hide != HIDE_IGNORE:
			control = self.browser.find_control(NAME_HIDE).get(set_hide).selected = True
		self.browser["wpReason"] = reason
		
		self.submit()
		return True

	###################
	##	Get CentralAuth Status
	##	required: setBaseUrl() to metawiki
	##	TERRIBLE HACKS HERE, be ye warned.
	###################
	def getCentralAuthStatus( self, user ):
		self.trace()
		self.login()

		# load form (terrible hacks here)
		self.load( title = 'Special:CentralAuth', parameters = {'target':user}, GET = True, visit = True, parse_as = 'html' )
		try:
			self.browser.select_form( predicate = lambda form: 'wpMethod' in [item.name for item in form.controls] and form['wpMethod'] == 'set-status' )
		except mechanize.FormNotFoundError:
			raise self.Error, 'could not find set-status form from Special:CentralAuth'
			
		# parse status
		NAME_LOCK = 'wpStatusLocked'
		NAME_HIDE = 'wpStatusHidden'
		LOCK_NO     = "0"
		LOCK_YES    = "1"
		HIDE_NO     = ""
		HIDE_IGNORE = None
		HIDE_LISTS  = "lists"
		HIDE_SUPPRESSED = "suppressed"
		
		is_locked = self.browser[NAME_LOCK][0]
		is_locked = True if (is_locked == LOCK_YES) else False
		
		is_hidden = self.browser[NAME_HIDE][0]
		is_hidden = True if (is_hidden in [HIDE_LISTS, HIDE_SUPPRESSED]) else False
		
		is_suppressed = True if (is_hidden == HIDE_SUPPRESSED) else False
		
		# return result
		return {
			'locked':is_locked,
			'hidden':is_hidden,
			'oversighted':is_suppressed
		}
		
	###################
	##	Get global rights
	###################
	def getGlobalRights( self, user ):
		self.trace()

		self.load( url = 'http://toolserver.org/~pathoschild/api/', parameters = {'action':'gblrights', 'user':user}, GET = True, parse_as = 'xml' )
		return self.stripHtml( self.parsed.getElementsByTagName('result')[0].getAttribute('info') )


	###################
	##	Global(Un)Block
	##	required: setBaseUrl() to metawiki
	###################
	def globalBlock( self, address, reason, expiry = None, lock = True, anononly = True ):
		self.trace()
		self.login()

		# find current blocks affecting this IP
		blocks = []
		for block in self.getGlobalBlocks( address ):
			blocks.append( block['address'] )
		count = len( blocks )
		if count:
			blocks_str = blocks[0] if count==1 else '[%s]' % ', '.join( blocks )
		collateral = ( count > 1 or (count and blocks_str != address) )

		# block
		if lock:
			if count:
				raise self.Error, 'That IP is already blocked%s' % ( ' as %s' % blocks_str if collateral else '' )

			# load form
			self.load( title = 'Special:GlobalBlock', visit = True, parse_as = 'html' )
			self.browser.select_form( name = 'uluser' )

			# fill in
			self.browser['wpAddress'] = address
			self.browser['wpReason']  = reason
			self.browser['wpExpiryOther'] = expiry
			self.browser.find_control( 'wpAnonOnly' ).items[0].selected = anononly
			self.submit()

		# unblock
		else:
			# not blocked
			if not count:
				raise self.Error, 'That IP is not blocked'

			# not directly blocked
			if address not in blocks:
				raise self.Error, 'That IP is not directly blocked (but it\'s blocked as %s)' % blocks_str

			# directly blocked, unblock
			else:
				# load form
				self.load( title = 'Special:GlobalUnblock', visit = True, parse_as = 'html' )
				self.browser.select_form( name = 'globalblock-unblock' )
				self.browser['address'] = address
				self.browser['wpReason'] = reason
				self.submit()

	def global_unblock( self, address, reason ):
		return self.globalBlock( address, reason, lock = False )


	###################
	##	Scan global account's local accounts
	##	required: setBaseUrl() to metawiki
	##	NOTE: synchronize changes with getGlobalEdits!
	###################
	def getGlobalAccounts( self, user, show_zero_edits = False ):
		self.trace()
		self.login()

		# load form
		self.load( title = 'Special:CentralAuth', parameters = {'target':user}, GET = True, parse_as = 'html' )

		# extract wiki rows
		fields = self.parsed.findAll( attrs = {'name':'wpWikis[]'} )

		# extract counts
		wikis = []
		for field in fields:
			wikis.append( field['value'] )

		# done
		return wikis


	###################
	## 	Scan global account's edits
	##	required: setBaseUrl() to metawiki
	##	NOTE: synchronize changes with getGlobalAccounts!
	###################
	def getGlobalEdits( self, user, show_zero_edits = False ):
		self.trace()
		self.login()

		# load form
		self.load( title = 'Special:CentralAuth', parameters = {'target':user}, GET = True, parse_as = 'html' )

		# extract wiki rows
		form = self.parsed.find( id = 'mw-centralauth-merged' )
		table = form.find( 'table' )
		rows = table.findAll( 'tr' )
		rows.pop( 0 )              # ignore header
		rows.pop( len(rows) - 1 )  # ignore footer

		# extract counts
		edits = {}
		for row in rows:
			fields = row.findAll( 'td' )
			wiki  = fields[1].find( 'a' ).string
			count = int( fields[5].find( 'a').string )

			if count>0 or show_zero_edits:
				edits[wiki] = count

		# done
		return edits


	###################
	##	Edit global wiki set
	##	required: setBaseUrl() to metawiki
	###################
	def wikiset( self, id, reason = None, add_wikis = None, del_wikis = None ):
		self.trace()
		self.login()

		if not add_wikis and not del_wikis:
			return

		# load form
		self.load( title = 'Special:EditWikiSets/%s' % id, visit = True, parse_as = 'html' )
		self.browser.select_form( predicate = lambda form: 'wpWikis' in [item.name for item in form.controls] )

		# change set
		wikis = self.browser['wpWikis'].splitlines()
		changed = False
		if add_wikis:
			for wiki in add_wikis:
				if wiki not in wikis:
					wikis.append( wiki )
					changed = True
		if del_wikis:
			for wiki in del_wikis:
				if wiki in wikis:
					wikis.remove( wiki )
					changed = True

		# set reason
		if reason:
			self.browser['wpReason'] = reason

		# submit
		if not changed:
			raise self.Error, 'no change needed'
		else:
			wikis.sort()
			self.browser['wpWikis'] = '\n'.join( wikis )

		# submit form
		self.submit()


	###########################################################################
	##	Non-MediaWiki queries (screen-scraping)
	###########################################################################
	###################
	##	Look up language code
	###################
	def lookupCode( self, code ):
		self.trace()

		# load page
		self.load( url = 'http://pathos.ca/tools/iso639db/', parameters = {'exact':'1', 'codes':'1', 'search':code}, parse_as = 'html', GET = True )

		# fetch rows
		rows = self.parsed.find( 'table' ).findAll( 'tr' )
		rows.pop( 0 ) # ignore header

		# parse results
		results = []
		for row in rows:
			fields = row.findAll( 'td' )

			results.append({
				'list': self.readXmlElement( fields[0] ),
				'code': self.readXmlElement( fields[1] ),
				'name': self.readXmlElement( fields[2] ),
				'scope':self.readXmlElement( fields[3] ),
				'type': self.readXmlElement( fields[4] ),
				'notes':self.readXmlElement( fields[5] )
			})
		return results


	###################
	##	Translation
	###################
	def translate( self, text, source = '', target = 'en' ):
		self.trace()

		#########
		## Validation
		#########
		# text
		if not text:
			return self.Error, 'must specify text'

		# language codes
		source = source.lower().strip()
		target = target.lower().strip()
		if source == target:
			raise self.Error, '...'
		if len(source) > 3 or len(target) > 3:
			raise self.Error, 'Please use valid two- or three-letter ISO 639 (1-3) language codes.'

		#########
		## Translate
		#########
		self.load(
			url        = 'http://ajax.googleapis.com/ajax/services/language/translate',
			parameters = {'v':1.0, 'q':text, 'langpair':'%s|%s' % (source, target)},
			GET        = True,
			parse_as   = 'json',
			catch_errors = False # doesn't know status codes
		)

		if self.parsed['responseStatus'] != 200:
			raise self.Error, 'Error %s: %s' % (self.parsed['responseStatus'], self.parsed['responseDetails'])
		result = self.parsed['responseData']['translatedText']
		if not source:
			source = self.parsed['responseData']['detectedSourceLanguage']

		#########
		## Translate
		#########
		return {
			'source_lang':source,
			'source_text':text,
			'target_lang':target,
			'target_text':result
		}
