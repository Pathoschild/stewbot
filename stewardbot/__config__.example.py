# -*- coding: utf-8  -*-
#######################################################
##	Configuration
##	Sets constants and settings used by the bot.
#######################################################
import re # regex

###################
## Overall configuration
###################
_INDEX_OPEN      = 0
_INDEX_USERS     = 1
_INDEX_OPERATORS = 2

config = {
	###################
	## IRC
	###################
	'irc':{
		# connection
		'server':'irc.freenode.net',
		'port':6667,
		'nick':'stewbotClone',
		'user':'ExampleUserName',
		'pass':'',
		'chans':['#stewardbot'],
		'ssl':False, # If you have this set to True, make sure you change the port to ssl port 7070 or 7000

		# options
		'confirm_all':0, # report all successes to channel (if another bot isn't reporting CentralAuth actions or global blocks)
		'quit_reason':'*poof*',
		'command_prefix':'!*',
		'command_delimiter':'<>',

		########
		## users
		########
		# regexes to match against full *!*@* masks
		'ignore_masks':[
			'@wikimedia/bot/SULWatcher',
			'@unaffiliated/az1568/bot/'
		],

		# level, hostmask, wiki lookup
		'wiki_names_by_level':{
			# whitelisted users (can issue some commands, ask for !commit on others)
			_INDEX_USERS:{
				# stewards
				'wikimedia/andre-engels':'Andre Engels',
				'wikimedia/Avraham':'Avraham',
				'wikimedia/Bastique':'Bastique',
				'wikipedia/darkoneko':'Darkoneko',
				'wikimedia/DerHexer':'DerHexer',
				'Wikimedia/Dferg':'Dferg',
				'wikimedia/Drini':'Drini',
				'wikimedia/dungodung':'Dungodungo',
				'wikimedia/effeietsanders':'Effeietsanders',
				'wikimedia/erwin':'Erwin',
				'wikimedia/guillom':'Guillom',
				'wikipedia/jdelanoy':'J.delanoy',
				'wikimedia/jhs':'Jon Harald Søby',
				'wikipedia/Jyothis':'Jyothis',
				'wikimedia/Kylu':'Kylu',
				'kamfjord.org':'Laaknor',
				'wikipedia/Mardetanha':'Mardetanha',
				'wikimedia/Melos':'Melos',
				'Wikimedia/Mercy':'Mercy',
				'wikibooks/mike.lifeguard':'Mike.lifeguard',
				'wikimedia/Millosh':'Millosh',
				'wikipedia/Nick1915':'Nick1915',
				'wikimedia/Shanel':'Shanel',
				'wikimedia/Sir-Lestaty-de-Lioncourt':'Sir Lestaty de Lioncourt',
				'wikipedia/sj':'Sj',
				'wikimedia/Thogo':'Thogo',
				'wikipedia/Wutsje':'Wutsje',

				# guests
				'wikia/vstf/countervandalism.user.Charitwo':'Charitwo',
				'wikimedia/Az1568':'Az1568',
				'wikipedia/Bsadowski1':'Bsadowski1',
				'wikipedia/Chris-G':'Chris G',
				'wikipedia/fr33kman':'Fr33kman',
				'wikimedia/GrooveDog':'GrooveDog',
				'wikimedia/Innv':'Innv',
				'wikimedia/Jamesofur':'Jamesofur',
				'wikia/vstf/countervandalism.user.Grunny':'Grunny',
				'Wikimedia/Kanonkas':'Kanonkas',
				'wikimedia/Kylu':'Kylu',
				'wikimedia/Maximillion-Pegasus':'Maximillion Pegasus',
				'wikimedia/MuZemike':'Muzemike',
				'wikimedia/Juliancolton':'Juliancolton',
				'wikipedia/NuclearWarfare':'NuclearWarfare',
				'wikimedia/pmlineditor':'Pmlineditor',
				'wikipedia/Prodego':'Prodego',
				'wiktionary/Razorflame':'Razorflame',
				'wikipedia/The-Thing-That-Should-Not-Be':'The Thing That Should Not Be',
				'wikipedia/Tiptoety':'Tiptoety'
			},
			# operators (full access)
			_INDEX_OPERATORS:{
				'wikimedia/Pathoschild':'Pathoschild',
				#'wikimedia/Shanel':'Shanel'
			}
		},

		########
		## commands
		########
		'commands_by_level':{
			_INDEX_OPEN:['help', 'activity', 'links', 'lookup', 'scanedits', 'showrights', 'translate', 'bash', 'debug', 'queue'],
			_INDEX_USERS:['config', 'exit', 'reset'],
			_INDEX_OPERATORS:['block', 'blockhide', 'checkuser', 'delete', 'lock', 'globaloversight', 'hide', 'lockhide', 'unlock', 'unhide', 'gblock', 'gunblock', 'setrights', 'stab', 'stabhide', 'unblock', 'wikiset', 'withlist', 'commit', 'cancel']
		},
		'commands_nocommit':['commit', 'cancel', 'checkuser', 'queue']
	},

	###################
	## Web
	###################
	'web':{
		# login & browser
		'user':'WIKI_USER_NAME',
		'pass':'WIKI_PASSWORD',
		'user_agent':'stewbot (meta.wikimedia.org/wiki/user:StewardBot)',

		# defaults
		'default_base_url':'http://meta.wikimedia.org',
		'default_prefix':'metawiki', # TODO: UNUSED
		'default_ca_reason':'Crosswiki abuse',
		'max_api_items':200, # TODO: UNUSED

		# misc
		'wikiset_ids':{
			2:'global_bots'
		}
	},

	###################
	## Debugging
	###################
	'debug':{
		'verbose':True,          # Trace function calls and interesting events to terminal
		'dump_exceptions':True,  # When an exception occurs, dump data useful to debugging the cause to a text file
		'dump_file':'/home/pathoschild/public_html/stewardbot/dump',    # File to dump exception data to
		'dump_url':'http://toolserver.org/~pathoschild/stewardbot/dump' # URL to dump file if world-readable (else None)
	}
}


###################
## Derived configuration
###################
# users by level
config['irc']['users_by_level'] = {
	_INDEX_USERS:config['irc']['wiki_names_by_level'][_INDEX_USERS].keys(),
	_INDEX_OPERATORS:config['irc']['wiki_names_by_level'][_INDEX_OPERATORS].keys()
}
config['irc']['users_by_level'][_INDEX_USERS].sort()
config['irc']['users_by_level'][_INDEX_OPERATORS].sort()

config['irc']['wiki_names'] = dict( config['irc']['wiki_names_by_level'][_INDEX_USERS] )
config['irc']['wiki_names'].update( config['irc']['wiki_names_by_level'][_INDEX_OPERATORS] )

# commands
config['irc']['commands'] = config['irc']['commands_by_level'][_INDEX_OPEN] + config['irc']['commands_by_level'][_INDEX_USERS] + config['irc']['commands_by_level'][_INDEX_OPERATORS]

################################
## IRC command documentation
################################
CONFIG_OPTIONS = ['confirm_all'] # used in "config" topic
documentation = {
	# special documentation
	None:'I\'m a steward utility script. See: \'!help access\', \'!help commands\', or \'!help status\'',
	'ACCESS':'commands are either open (anyone can issue them), whitelisted (whitelisted users only), or restricted (only operators, or whitelisted users if an operator !commit\'s them)',
	'ACCESSLIST':'operators: [%s]; whitelisted users: [%s]' % (', '.join(config['irc']['wiki_names_by_level'][_INDEX_OPERATORS].values()), ', '.join(config['irc']['wiki_names_by_level'][_INDEX_USERS].values())),
	'commands':'recognized commands: open [%s]; whitelisted [%s]; restricted [%s]. Say \'!help command_here\' for help on a specific command' % (', '.join(config['irc']['commands_by_level'][_INDEX_OPEN]), ', '.join(config['irc']['commands_by_level'][_INDEX_USERS]), ', '.join(config['irc']['commands_by_level'][_INDEX_OPERATORS])),

	# meta-commands
	'help':'displays concise documentation; type \'!help\' for details and syntax',
	'config':{
		None:'changes runtime configuration. Syntax is \'!config option > value\'. Available configuration options: %s (see \'!help config > option_here\')' % CONFIG_OPTIONS,
		'confirm_all':'always display confirmation messages (redundant when StewardBot is active). Syntax is "!config confirm_all > 0|1"'
	},
	'commit':'perform a queued command. Syntax is \'!commit id\' or \'!commit start_id:end_id\' or \'!commit all\'; with an optional third argument \'verbose\', repeats the command being performed',
	'cancel':'cancel a queued command. Syntax is \'!cancel id\'  or \'!cancel start_id:end_id\' or \'!cancel all\'; with an optional third argument \'quiet\', does not notify users of cancelled commands',
	'queue':'view the command queue; syntax is \'!queue\' or \'!queue commit_id\'',

	# information
	'scanedits':'scan a global user\'s local accounts for edits; syntax is \'!scanedits name\'',
	'showrights':'list the specified user\'s local and global right-groups. Syntax is \'!showrights user\'',
	'activity':'get dates of last edit, local sysop action, and local bureaucrat action on the specified wiki; syntax is \'!activity dbprefix or domain\'',
	'lookup':'look up information on the language code. Syntax is \'!lookup code\'',
	'translate':'translate text from one language to another. Syntax is \'!translate text\' (autodetect to English), \'!translate target_code > text\' (target to English), or \'!translate source_code > target_code > text\'',
	'bash':'say a quote selected from <http://meta.wikimedia.org/wiki/Bash>, <https://bugzilla.wikimedia.org/quips.cgi?action=show>, or IRC; syntax is \'!bash\' (random), \'!bash literal search terms\' (first matching quote), or \'!bash id\' (get quote by queue ID)',

	# centralAuth
	'lock':'lock a global account; syntax is \'!lock name\' or \'!lock name > reason\'',
	'hide':'hide a global account; syntax is \'!hide name\' or \'!hide name > reason\'',
	'lockhide':'lock and hide a global account; syntax is \'!lockhide name\' or \'!lockhide name > reason\'',
	'globaloversight':'Lock and hide a global account, and oversight its local name on all local wikis (this will oversight them in edit histories, which may violate the oversight policy; use with care); syntax is \'!globalOversight name\'',
	'unlock':'unlock a global account; syntax is \'!unlock name\' or \'!unlock name > reason\'',
	'unhide':'unhide a global account; syntax is \'!unhide name\' or \'!unhide name > reason\'',

	# other restricted
	'block':'block the given local account; syntax is \'!block user@wiki\' or \'!block user@wiki > expiry\' or \'!block user@wiki > expiry > reason\'. Expiry can be \'never\' or a GNU time, and wiki can \'global\' or a database prefix',
	'blockhide':'block the given local account, and suppress the name from logs and edit histories; syntax is \'!blockhide user@wiki\' or \'!blockhide user@wiki > reason\'. Wiki can be \'global\' or a database prefix',
	'unblock':'unblock the given local account; syntax is \'!unblock user@wiki\' or \'!unblock user@wiki > reason\'. Wiki can be \'global\' or a database prefix',
	'delete':'delete the given page title; syntax is \'!delete title@wiki > reason\', where wiki is a database prefix',
	'checkuser':'grant the requesting user checkuser access on the wiki, and link to the prefilled Checkuser form; restricted to operators; syntax is \'!checkuser check_target@wiki\'',
	'gblock':'globally block an IP address or CIDR range, anonymous-users only; syntax is \'!gblock address > expiry > reason\'',
	'gunblock':'globally unblock an IP address or CIDR range; syntax is \'!gunblock address > reason\'',
	'stab':'lock & hide global account, scan edits, and block all local accounts; syntax is \'!stab name\'',
	'stabhide':'lock & hide global account, scan edits, block all local accounts, and oversight name in local logs and edit histories; syntax is \'!stabhide name\'',
	'withlist':'Parse a plaintext newline-delimited list of values at the given URL, and queue \'!command > value > arguments\' for each value (!commit\'s needed); syntax is \'!withlist url > command > arguments...\'',
	'wikiset':'Add or remove wikis in a wikiset; syntax is \'!wikiset id > +wiki,wiki,-wiki\' or \'!wikiset id > wiki > reason\', where id is one of [%s]' % ','.join(['%s=%s' % (k,v) for k,v in config['web']['wikiset_ids'].items()]),

	# irc-only commands
	'links':'provide relevant links for IPs or global accounts; syntax is \'!links ip or name\'',

	# other
	'exit':'disconnect from IRC and end process; syntax is \'!exit\' or \'!exit quit reason\'',
	#'nuke':'revert all edits and moves by a user, and delete page creations',
	'reset':'clear web sessions, reset base URL, disconnect from IRC and reconnect; syntax is \'!reset\' or \'!reset quit reason\'',
	'setrights':'add or remove a user\'s right-groups. Groups are listed with commas, and by default each group is added. Add \'+\' or \'-\' before a name to switch between addition and removal for subsequent groups. Syntax is \'!setrights user > +right1,right2,-right3\' or \'!setrights user > +right1,-right2,+right3 > reason\'',
}
