"""
	Generic library of functions for encoding, decoding, and manipulating strings.
	@author Jesse Plamondon-Willard
"""
import urllib
import stewbot.components.modules.chardet as chardet

class Formatting(object):
	@classmethod

	def Decode(cls, input, encodings=['utf-8', 'ISO-8859-1', 'CP1252', 'latin1']):
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
				except UnicodeDecodeError:
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
			try:
				return Formatting.Decode(str(input))
			except UnicodeDecodeError:
				raise UnicodeDecodeError, 'Cannot decode non-string object with Unicode representation "%s".' % repr(
					input)

	@classmethod
	def Encode(cls, obj, encoding='utf-8'):
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
			obj = Formatting.Decode(obj)
		return obj.encode(encoding)

	@classmethod
	def UrlEncode(cls, obj):
		"""
		Convert the dict into an escaped HTTP query string, without the leading
		? character.

		@param obj: dict to parse.
		@return str: encoded URL query string.
		"""
		newObj = {}
		for k in obj.keys():
			newObj[Formatting.Encode(k)] = Formatting.Encode(obj[k])
		return urllib.urlencode(newObj)
