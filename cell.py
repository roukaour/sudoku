from __future__ import print_function

from utils import *
from color import *

class Cell(object):
	"""A cell on a 9x9 Sudoku board."""

	VALUES = range(1, 10)
	ROWS = 'ABCDEFGHJ'
	COLS = '123456789'
	BLOCKS = '123456789'

	def __init__(self, x, y, ds=None):
		self.x = x
		self.y = y
		self.b = y // 3 * 3 + x // 3
		if isinstance(ds, Cell):
			self.ds = set(ds.ds)
		elif isinstance(ds, (list, tuple, set)):
			self.ds = set(ds)
		elif ds in Cell.VALUES or ds in map(str, Cell.VALUES):
			self.ds = {int(ds)}
		else:
			self.ds = set(Cell.VALUES)
		self.dcs = {}

	def __str__(self):
		return '%s = {%s}' % (self.cell_name(),
			', '.join(self.dcs.get(d, Color.NEITHER).colored(d) for d in sorted(self.ds)))

	def __repr__(self):
		return 'Cell(%d, %d, {%s})' % (self.x, self.y,
			', '.join(self.dcs.get(d, Color.NEITHER).colored(d) for d in sorted(self.ds)))

	def __lt__(self, other):
		return (self.y, self.x) < (other.y, other.x)

	def row_name(self):
		return Cell.ROWS[self.y]

	def col_name(self):
		return Cell.COLS[self.x]

	def block_name(self):
		return Cell.BLOCKS[self.b]

	def unit_name(self, unit_type):
		unit_names = {
			'row': self.row_name,
			'column': self.col_name,
			'block': self.block_name}
		return unit_names[unit_type]()

	def cell_name(self):
		return self.row_name() + self.col_name()

	def solved(self):
		return len(self.ds) == 1

	def bi_value(self):
		return len(self.ds) == 2

	def value(self):
		return list(self.ds)[0] if self.solved() else '.'

	def value_string(self):
		return str(self.value()) if self.solved() else set_string(self.ds)

	def exclude(self, ds):
		"""Exclude the given candidates and return whether any were eliminated."""
		n = len(self.ds)
		self.ds -= set(ds)
		return len(self.ds) < n

	def include_only(self, ds):
		"""Include only the given candidates and return whether any were eliminated."""
		n = len(self.ds)
		self.ds &= set(ds)
		return len(self.ds) < n
