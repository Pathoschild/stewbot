import inspect

class Interface(object):
	"""
	Static class responsible for pythonic interfaces and implementation
	validation.
	
	Example usage:
	foo = SomeClass()
	Interface.Assert(foo, IFoo) # foo implements IFoo, or InterfaceException.
	"""
	
	@staticmethod
	def Assert(obj, interface):
		"""
		Verify that Object defines every method in Interface, and every method
		accepts the same argument keywords. Any method whose name starts with an
		underscore is ignored (convention for a private method).
		
		@param obj: class instance to check against the interface.
		@param interface: class interface to check the class against.
		"""
		i_method_names = [method for method in dir(interface) if callable(getattr(interface, method)) and method[0] is not '_']
		o_method_names = [method for method in dir(obj) if callable(getattr(obj, method)) and method[0] is not '_']
		
		for i_name in i_method_names:
			# method exists?
			if i_name not in o_method_names:
				raise InterfaceException, 'Object %s does not match required interface %s: method \'%s\' not found' % (obj, interface, i_name)
			
			# arguments match?
			i_args = inspect.getargspec(getattr(interface, i_name))
			o_args = inspect.getargspec(getattr(obj, i_name))
			i_default_count = (0 if i_args[3] is None else len(i_args[3]))
			o_default_count = (0 if o_args[3] is None else len(o_args[3]))
			i_required_count = len(i_args[0]) - i_default_count
			o_required_count = len(o_args[0]) - o_default_count

			if o_required_count is not i_required_count or o_default_count is not i_default_count:
				raise InterfaceException, 'Object %s does not match required interface %s: method \'%s\' has a different positional or keyword argument count: found (%s), but expected (%s)' % (obj, interface, i_name, Interface._GetArgString(o_args), Interface._GetArgString(i_args))
	
	@staticmethod
	def _GetArgString(args):
		# merge defaults into arguments
		_args = [arg for arg in args[0]]
		if args[3] is not None:
			arg_c = len(_args) - 1
			for i in range(0, len(args[3])):
				_args[arg_c - i] += "=%s" % args[3][i]
		return ", ".join(_args)


class InterfaceException(Exception):
	"""Exception thrown when an object does not implement an expected interface."""

#class Bash(object):
#	def get(self, id, boop, zoop, poop, zoozp):
#		pass

#class IBash(object):
#	def get(self, id, boop, zoop=3, poop=7):
#		pass
		
## test stuff
#foo = Bash()
#Interface.Assert(Bash, IBash)