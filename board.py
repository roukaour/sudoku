from __future__ import print_function

from utils import *
from color import *
from cell import *

from collections import namedtuple
from itertools import product
from functools import wraps

Strategy = namedtuple('Strategy', ('name', 'function'))

class Sudoku(object):
	"""A 9x9 Sudoku board."""

	UNIT_TYPES = ['row', 'column', 'block']

	# A dictionary of solution strategies, keyed by their increasing difficulty
	strategies = {0: Strategy('nothing', lambda sudoku, verbose: False)}

	@classmethod
	def strategy(cls, name, difficulty):
		"""Decorate a strategy function to register it for use in the solve method."""
		def decorator(function):
			@wraps(function)
			def wrapper(sudoku, verbose):
				if sudoku.solved():
					return False
				if verbose:
					print('Try', name)
				changed = function(sudoku, verbose)
				if verbose and not changed:
					print('...No', name, 'found')
				return changed
			cls.strategies[difficulty] = Strategy(name, wrapper)
			return wrapper
		return decorator

	def __init__(self, *cells):
		if len(cells) == 1:
			cells = cells[0]
			if isinstance(cells, str):
				cells = filter(None, (c if c in map(str, Cell.VALUES) else
					'0' if c in '0._*' else '' for c in cells))
			cells = list(cells)
		if len(cells) == 9:
			cells = flatten(map(list, cells))
		if len(cells) != 81:
			raise ValueError('Invalid Sudoku board: %r' % (cells,))
		self.cm = []
		while cells:
			row, cells = cells[:9], cells[9:]
			row = [Cell(i, len(self.cm), d) for i, d in enumerate(row)]
			self.cm.append(row)

	def __repr__(self):
		return 'Sudoku(%r)' % self.code_str()

	def __str__(self):
		return self.terse_str() if self.solved() else self.verbose_str()

	def code_str(self):
		return ''.join(str(c.value()) for c in self.cells())

	def terse_str(self):
		return '''    1 2 3   4 5 6   7 8 9
  +-------+-------+-------+
A | %s %s %s | %s %s %s | %s %s %s |
B | %s %s %s | %s %s %s | %s %s %s |
C | %s %s %s | %s %s %s | %s %s %s |
  +-------+-------+-------+
D | %s %s %s | %s %s %s | %s %s %s |
E | %s %s %s | %s %s %s | %s %s %s |
F | %s %s %s | %s %s %s | %s %s %s |
  +-------+-------+-------+
G | %s %s %s | %s %s %s | %s %s %s |
H | %s %s %s | %s %s %s | %s %s %s |
J | %s %s %s | %s %s %s | %s %s %s |
  +-------+-------+-------+''' % tuple(c.value() for c in self.cells())

	def verbose_str(self):
		s = flatten(list('   (%d)   ' % c.value()) if c.solved() else
			[c.dcs.get(d, Color.NEITHER).colored(d) if d in c.ds else '.'
				for d in Cell.VALUES] for c in self.cells())
		return ('''     1   2   3     4   5   6     7   8   9
  +-------------+-------------+-------------+
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
A | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  |             |             |             |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
B | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  |             |             |             |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
C | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  +-------------+-------------+-------------+
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
D | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  |             |             |             |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
E | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  |             |             |             |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
F | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  +-------------+-------------+-------------+
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
G | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  |             |             |             |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
H | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  |             |             |             |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
J | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s | %s%s%s %s%s%s %s%s%s |
  +-------------+-------------+-------------+''' %
		tuple(flatten(flatten(flatten(transpose(chunk(chunk(h, 3), 3))
			for h in chunk(s, 81))))))

	def verify(self):
		verified = True
		values = set(Cell.VALUES)
		for i in range(9):
			verified &= union(c.ds for c in self.row(i)) == values
			verified &= union(c.ds for c in self.col(i)) == values
			verified &= union(c.ds for c in self.block(i)) == values
		for y, x in product(range(9), range(9)):
			cell = self.cell(x, y)
			verified &= 1 <= len(cell.ds) <= 9 and cell.ds.issubset(values)
		if not verified:
			raise RuntimeError('Sudoku board is in an invalid state')

	def copy(self):
		return Sudoku(*self.cm)

	def cells(self):
		return flatten(self.cm)

	def row(self, y):
		return self.cm[y]

	def row_without(self, x, y):
		return self.cm[y][:x] + self.cm[y][x+1:]

	def col(self, x):
		return [row[x] for row in self.cm]

	def col_without(self, x, y):
		return [row[x] for i, row in enumerate(self.cm) if i != y]

	def block(self, i):
		y, x = divmod(i, 3)
		return list(flatten(self.cm[3*y+i][3*x:3*x+3] for i in range(3)))

	def block_without(self, x, y):
		bx3, by3 = x // 3 * 3, y // 3 * 3
		return list(self.cm[by3+i][bx3+j] for i in range(3) for j in range(3)
			if by3+i != y or bx3+j != x)

	def unit(self, unit_type, i):
		units = {
			'row': self.row,
			'column': self.col,
			'block': self.block}
		return units[unit_type](i)

	def unit_without(self, unit_type, x, y):
		units_without = {
			'row': self.row_without,
			'column': self.col_without,
			'block': self.block_without}
		return units_without[unit_type](x, y)

	def seen_from(self, x, y):
		row = self.row_without(x, y)
		col = self.col_without(x, y)
		block = self.block_without(x, y)
		return set(row + col + block)

	def cell_block(self, x, y):
		return self.block(y // 3 * 3 + x // 3)

	def cell(self, x, y):
		return self.cm[y][x]

	def row_name(self, y):
		return Cell.ROWS[y]

	def col_name(self, x):
		return Cell.COLS[x]

	def block_name(self, i):
		return Cell.BLOCKS[i]

	def unit_name(self, unit_type, i):
		unit_names = {
			'row': self.row_name,
			'column': self.col_name,
			'block': self.block_name}
		return unit_names[unit_type](i)

	def solved(self):
		return all(c.solved() for c in self.cells())

	def num_solved(self):
		return len([c for c in self.cells() if c.solved()])

	def solve(self, max_difficulty=None, exclude=None, include_only=None, verbose=False):
		"""Try to solve any unsolved cells with all registered strategies."""
		if verbose:
			print(self.terse_str())
		if verbose:
			print('Solving:', self.code_str())
		num_solved = self.num_solved()
		difficulty = 0
		last_difficulty = -1
		while last_difficulty:
			last_difficulty = self._solve_strategies(max_difficulty, exclude, include_only, verbose)
			difficulty = max(difficulty, last_difficulty)
		if verbose:
			print('Completely solved!' if self.solved() else '...Cannot solve further',
				'(solved %d cells)' % (self.num_solved() - num_solved))
			print('Most advanced strategy used:', self.strategies[difficulty].name)
			print('Solved:', self.code_str())
			print(self)
		return self.strategies[difficulty].name

	def _solve_strategies(self, max_difficulty=None, exclude=None, include_only=None, verbose=False):
		"""Try all registered strategies in order of increasing difficulty."""
		if self.solved():
			return 0
		for difficulty, strategy in sorted(self.strategies.items()):
			if ((max_difficulty is not None and difficulty > max_difficulty) or
				(exclude is not None and difficulty in exclude) or
				(include_only is not None and difficulty not in include_only)):
				continue
			if strategy.function(self, verbose):
				return difficulty
		return 0
