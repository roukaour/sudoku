from __future__ import print_function

import sys

class Color(object):
	"""A printable and mixable color."""

	# A dictionary of all colors, keyed by their numeric value
	colors = {}

	def __init__(self, value, name, code):
		self.value = value
		self.name = name
		self.code = code
		Color.colors[value] = self

	def __repr__(self):
		return 'Color(%d, %r, %r)' % (self.value, self.name, self.code)

	def __str__(self):
		return self.colored(self.name)

	def __nonzero__(self):
		return bool(self.value)

	def __invert__(self):
		return Color.colors[~self.value]

	def __and__(self, other):
		return Color.colors[self.value & other.value]

	def __or__(self, other):
		return Color.colors[self.value | other.value]

	def colored(self, s):
		if sys.platform != 'win32':
			return '\x1b[%sm%s\x1b[0m' % (self.code, s)
		return s

Color.NEITHER = Color(0, 'neither', '0')
Color.RED = Color(1, 'red', '31;1')
Color.BLUE = Color(~1, 'blue', '44')
Color.PURPLE = Color(~0, 'purple', '37;45;1')

# RED == ~BLUE
# BLUE == ~RED
# PURPLE == RED | BLUE
# NEITHER == RED & BLUE
