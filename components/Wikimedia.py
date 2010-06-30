#######################################################
##	Wikimedia.Browser
##	Extends Browser with methods for listing or linking to Wikimedia wikis,
##	converting between prefixes and URL, and checking whether a wiki is locked
##	or internal. Fetches list of wikis from site matrix.
#######################################################
import os
import pickle
import re
import time
from Browser import Browser as BaseBrowser

class Browser( BaseBrowser ):
	###########################################################################
	##	Constructor
	##	Build lists of wikis
	###########################################################################
	def __init__( self, username, password, user_agent = 'stewbot framework', default_base_url = 'http://meta.wikimedia.org', default_index_path = '/w/index.php', default_api_path = '/w/api.php', obey_robot_rules = False, max_api_items = 200, wiki_cache = os.path.dirname(__file__) + '/Wikimedia.cache', max_cache_age = 14 * 24 * 60 * 60, load_wikis = True, logger = None ):
		BaseBrowser.__init__( self, username, password, user_agent, obey_robot_rules, max_api_items, logger = logger )
		self.trace(overrides = {'password':'<<hidden>>'})
		self.setBaseUrl( default_base_url, default_index_path, default_api_path, set_default = True )

		# define properties
		self.WIKI_CACHE    = wiki_cache
		self.MAX_CACHE_AGE = max_cache_age
		(self.CODE, self.FAMILY, self.DOMAIN, self.SPECIAL, self.LOCKED, self.PRIVATE) = (0,1,2,3,4,5) #indexes in wiki tuple

		self.families = []  # list of defined families
		self.languages = {} # lang code => name lookup
		self.domains = {}   # domain => prefix lookup
		self.wikis = {}     # prefix => (data) lookup

		# load wikis
		if load_wikis:
			self.loadWikis()
			logger.Log(self.families)


	###########################################################################
	##	Public interface
	###########################################################################
	###################
	## Load list of wikis
	###################
	def loadWikis( self, from_cache = True ):
		self.trace()

		# get wikis from cache (if allowed, file exists, and not too old)
		if from_cache and os.path.isfile( self.WIKI_CACHE ):
			cur_time   = time.mktime( time.localtime() )
			cache_time = os.path.getmtime( self.WIKI_CACHE )
			if cur_time - cache_time < self.MAX_CACHE_AGE:
				self.readCache()
				return

		# query API
		self.queryApi({
			'format':'json',
			'action':'sitematrix'
		})

		# parse specials
		for wiki in self.parsed['sitematrix']['specials']:
			self.storeWiki(
				code    = wiki['code'],
				family  = 'wiki',
				domain  = wiki['url'].replace('http://', ''),
				special = True
			)
		del self.parsed['sitematrix']['specials']
		del self.parsed['sitematrix']['count']

		# parse list
		for i in self.parsed['sitematrix']:
			lang = self.parsed['sitematrix'][i]
			self.languages[lang['code']] = lang['name']
			for wiki in lang['site']:
				self.storeWiki(
					code   = lang['code'].replace( '-', '_' ),
					family = wiki['code'],
					domain = wiki['url'].replace('http://', '')
				)

		# cache data and discard raw result
		self.writeCache()
		del self.parsed


	###################
	## Get wiki data
	###################
	def getWiki( self, code = None, family = None, domain = None, prefix = None, want = None ):
		self.trace()

		# fetch data
		data = ()
		if prefix:
			try:
				prefix = prefix.replace( '-', '_' ).replace( 'wikipedia', 'wiki' )
				data = self.wikis[prefix]
			except KeyError:
				raise self.Error, u'There is no wiki with the database prefix "%s"' % prefix

		elif domain:
			try:
				domain = document.replace( 'http://', '' )
				prefix = self.domains[domain]
				data = self.wikis[prefix]
			except KeyError:
				raise self.Error, u'There is no wiki with the domain "%s"' % domain

		else:
			try:
				code   = code.replace( '-', '_' )
				family = family.replace( 'wikipedia', 'wiki' )
				data = self.wikis[code + family]
			except KeyError:
				raise self.Error, u'The "%s" family has no "%s" wiki' % (family, code)

		# return data
		if want:
			return data[want]
		return data


	###################
	## Get wiki URL
	###################
	def getUrl( self, code = None, family = None, domain = None, prefix = None, path = None ):
		self.trace()

		domain = self.getWiki( code, family, domain, prefix, want = self.DOMAIN )

		if path == None:
			path = self.path_article
		return 'http://%s%s' % (domain, path)


	###################
	## reset
	###################
	def reset( self ):
		self.trace()
		super( Browser, self ).reset()
		self.loadWikis( from_cache = False )

	###################
	## Store wiki data
	###################
	def storeWiki( self, code, family, domain, special = False, locked = False, private = False ):
		self.trace()

		code   = code.replace( '-', '_' )
		domain = domain.replace( 'http://', '' )

		self.wikis[code + family] = (code, family, domain, special, locked, private)
		self.domains[domain] = code + family
		if family not in self.families:
			self.families.append( family )


	###################
	## Save wiki data to cache
	###################
	def writeCache( self ):
		self.trace()

		CACHE = open( self.WIKI_CACHE, 'w' )
		pickle.dump( (self.families, self.languages, self.domains, self.wikis), CACHE )


	###################
	## Read wiki data from cache
	###################
	def readCache( self ):
		self.trace()

		CACHE = open( self.WIKI_CACHE, 'r' )
		(self.families, self.languages, self.domains, self.wikis) = pickle.load( CACHE )
