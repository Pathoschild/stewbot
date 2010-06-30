## 
#	Generic library of functions for encoding, decoding, and manipulating strings.
#		Written by Jesse Plamondon-Willard, last updated 2010-06-30.
## 
import urllib

def Decode(input, encodings = ['utf-8', 'ISO-8859-1', 'CP1252', 'latin1']):
	"""
	Decode the arbitrary input string into a standard Unicode string.
	
	@param input: string to parse.
	@keyword encoding: list of strings representing encodings to prefer when attempting to decode the string.
	@return unicode: decoded string.
	"""
	if isinstance(input, unicode):
		return input
	elif isinstance(input, str):
		# can it be decoded using a preferred encoding?
		for encoding in encodings:
			try:
				return input.decode(encoding)
			except UnicodeDecodeError, e:
				continue
			
		# didn't work; try encoding detection heuristics
		try:
			return input.decode(chardet.detect(input))
		except UnicodeDecodeError:
			pass
		
		# OH NOES NOTHING IS WORKING!!!
		# maybe we can pretend it's okay?
		return input
	else:
		return Decode(str(input))


def Encode(obj, encoding = 'utf-8'):
	"""
	Encode the arbitrary input string into a raw UTF-8 bytestring. This is
	necessary when passing text to a third-party module, because most modules
	are incapable of processing decoded text.
	
	@param obj: string to parse.
	@keyword encoding: The encoding to cast the string to, if not UTF-8. 
	Changing this to something other than UTF-8 may cause encoding crashes
	if the string contains characters the encoding does not contain.
	@return str: encoded string.
	"""
	if not isinstance(obj, unicode):
		obj = Decode(obj)
	return obj.encode(encoding)


def UrlEncode(obj):
	"""
	Convert the dict into an escaped HTTP query string, without the leading
	? character.
	
	@param obj: dict to parse.
	@return str: encoded URL query string.
	"""
	newObj = {}
	for k in obj.keys():
		newObj[Encode(k)] = Encode(obj[k])
	return urllib.urlencode(newObj)