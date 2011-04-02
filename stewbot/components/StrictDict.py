#######################################################
##	StrictDict
##	Extends the dictionary type to provide validated access to its properties,
##	ensuring that new keys are not added accidentally and allowing dotted property
##	access.
#######################################################

class StrictDict( dict ):
	###################
	## Constructor
	###################
	def __init__( self, initDict = None, name = 'StrictDict' ):
		self.add( '__name__', name )
		if initDict:
			self.consumeDict( initDict )


	###################
	## Alias foo.key to foo[key]
	###################
	def __getattr__( self, key ):
		return self.__getitem__( key )

	def __setattr__( self, key, value ):
		return self.__setitem__( key, value )


	###################
	## Handle foo.key (get)
	###################
	def __getitem__( self, key ):
		if not self.has_key(key):
			raise AttributeError, 'Cannot read %s[\'%s\'] because the key is not defined.' % (self.__name__, key)
		return dict.__getitem__( self, key )


	###################
	## Handle foo.key = value
	###################
	#noinspection PyMethodOverriding
	def __setitem__( self, key, value, _override = False ):
		if not _override and not self.has_key(key):
			if not self.has_key('__name__'):
				self.add( '__name__', '<undef>' )
			raise AttributeError, 'Cannot modify %s[\'%s\'] because the key is not defined. To add a new key, use %s.add(\'%s\', value).' % (self.__name__, key, self.__name__, key)
		dictItems = self._getItemsOrFalse(value)
		if dictItems is False:
			dict.__setitem__( self, key, value )
		else:
			dict.__setitem__( self, key, StrictDict(value, name = '%s[\'%s\']' % (self.__name__, key)) )


	###################
	## Override iterators to ignore __name__
	###################
	def keys(self):
		return [key for key in dict.keys(self) if key != '__name__']

	def items(self):
		return [(key, value) for (key, value) in dict.items(self) if key != '__name__']

	def values(self):
		return [value for (key, value) in dict.items(self) if key != '__name__']

	def iterkeys(self):
		return dict.iterkeys(dict(self.items()))

	def itervalues(self):
		return dict.itervalues(dict(self.items()))

	def __iter__(self):
		return dict.__iter__(dict(self.items()))


	###################
	## Write value to a key, skipping key-exists validation
	###################
	def add( self, key, value ):
		return self.__setitem__( key, value, _override = True )


	###################
	## Consume a dictionary
	###################
	def consumeDict( self, obj ):
		items = self._getItemsOrFalse(obj)

		## not a dict!
		if not items:
			raise TypeError, 'StrictDict cannot consume a non-dictionary object'

		## consume
		else:
			for (k,v) in items:
				self.__setitem__( k, v, _override = True )
			return True


	###################
	## Get array of (key, value) if it's a dictionary, else False
	###################
	def _getItemsOrFalse(self, obj):
		try:
			return obj.items()
		except AttributeError:
			return False

	###################
	## Return dict equivalent of self
	###################
	def toDict( self ):
		return self._toDict( self )

	def _toDict( self, oldDict ):
		items = self._getItemsOrFalse( oldDict )

		## not a dict, return as-is
		if not items:
			return oldDict

		## dict, convert
		else:
			newDict = {}
			for (k,v) in items:
				newDict[k] = self._toDict( v )
			return newDict
