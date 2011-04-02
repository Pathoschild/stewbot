import inspect

class InterfaceException(Exception):
	"""Exception thrown when an object does not implement an expected interface."""

class Interface(object):
	@classmethod

	def Assert(cls, obj, interface):
		"""
		Verify that the object defines every property and  method in the
		interface, and every method accepts the same argument keywords. Any
		property or method whose name starts with an underscore is ignored
		(convention for a private method).

		@param obj: class instance to check against the interface.
		@param interface: class interface to check the class against.
		@return None
		@raise Interface.InterfaceExcept: raised when the object does not
			   implement the interface.
		"""

		i_dir = [item for item in dir(interface) if item[0] is not '_']
		o_dir = [item for item in dir(obj) if item[0] is not '_']

		for name in i_dir:
			# get interface details
			i_attr = getattr(interface, name)
			i_callable = callable(i_attr)#inspect.ismethod(i_attr) or inspect.isfunction(i_attr)

			# get object details
			if name not in o_dir:
				raise InterfaceException, 'Object %s does not match required interface %s: object does not implement %s \'%s\'' % (
				obj, interface, "method" if i_callable else "property", name)
			o_attr = getattr(obj, name)
			o_callable = callable(o_attr)#inspect.ismethod(o_attr) or inspect.isfunction(o_attr)

			# get details

			# type mismatch?
			if i_callable != o_callable:
				raise InterfaceException, 'Object %s does not match required interface %s: %s \'%s\' must be a %s' % (
				obj, interface, "method" if o_callable else "property", name, "method" if i_callable else "property")

			# signature mismatch
			if i_callable:
				i_args = inspect.getargspec(i_attr)
				o_args = inspect.getargspec(o_attr)
				i_default_count = (0 if i_args[3] is None else len(i_args[3]))
				o_default_count = (0 if o_args[3] is None else len(o_args[3]))
				i_required_count = len(i_args[0]) - i_default_count
				o_required_count = len(o_args[0]) - o_default_count

				if o_required_count is not i_required_count or o_default_count is not i_default_count:
					raise InterfaceException, 'Object %s does not match required interface %s: method \'%s\' has a different positional or keyword argument count: found (%s), but expected (%s)' % (
					obj, interface, name, Interface._GetArgString(o_args), Interface._GetArgString(i_args))


	@classmethod
	def _GetArgString(cls, args):
		# merge defaults into arguments
		_args = [arg for arg in args[0]]
		if args[3] is not None:
			arg_c = len(_args) - 1
			for i in range(0, len(args[3])):
				_args[arg_c - i] += "=%s" % args[3][i]
		return ", ".join(_args)
