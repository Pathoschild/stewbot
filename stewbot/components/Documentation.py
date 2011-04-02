# -*- coding: utf-8  -*-
#######################################################
##	Documentation
##	Abstracts documentation using an n-dimensioned hash.
##
##	Documentation( hash )
##		Construct instance given a hash of documentation strings, with
##		topic=>documentation mappings. Sub-topics can be specified as
##		topic=>hash mappings, and a default documentation for a
##		subtopic can be specified with the None key.
##		Example:
##		{
##			'meow':'Says "meow"',
##			'bark':'Says "woof"',
##			'yell':{
##				None:'Yells something; valid arguments: meow, woof',
##				'foo':'Says "FOO!!!"',
##				'bar':'Says "BAR!!!"'
##			}
##		}
##	get( [keys array] )<str>
##		Returns the string in the tree at the given keys, or
##		raises an error.
##		Examples:
##			get( [meow] ) # Says "meow"
##			get( [yell] ) # Yells something; valid arguments: meow, woof
##			get( [yell, foo] ) # Says FOO!!!
##
#######################################################
from copy import copy
from stewbot.components.BaseClass import BaseClass

###################
## Stewardbot class
###################
class Documentation( BaseClass ):
	#############################################################################################################
	##	Constructor
	##	Internally store response tree.
	#############################################################################################################
	def __init__( self, tree, logger, default = None ):
		BaseClass.__init__( self, logger = logger )
		self.trace()
		self.tree    = copy( tree )
		self.default = default

	###################
	## Exceptions
	###################
	class NoDefaultException( Exception ):
		""" No arguments given to get(), and no default response defined. """
	class NoSuchKeyException( Exception ):
		""" There is no response for the given topic. """

	###################
	## get
	## Returns the string in the tree at the given keys, or raises an error.
	###################
	def get( self, keys, default = None ):
		self.trace()

		# handle no keys
		if not len(keys):
			if default:
				return default
			elif self.default:
				return self.default
			elif self.tree[None]:
				return self.tree[None]
			else:
				raise self.NoDefaultException, 'No arguments given, and no default response defined.'

		# fetch keys
		subtree = self.tree
		found = 0

		for key in keys:
			key = key.lower().strip()
			try:
				if key in subtree:
					subtree = subtree[key]
					found   = 1
					continue
				break
			except TypeError:
				break

		# fetch text
		if found:
			try:
				return subtree[None]
			except TypeError:
				return subtree
		else:
			raise self.NoSuchKeyException, 'There is no response for the given topic.'
