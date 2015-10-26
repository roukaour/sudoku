#!/usr/bin/python

from __future__ import print_function

from itertools import product, combinations

def flatten(L):
	return [i for x in L for i in x]

def chunk(L, n):
	return zip(*[iter(L)] * n)

def transpose(L):
	return zip(*L)

def set_string(s):
	return '{' + ', '.join(map(str, sorted(s))) + '}'

def n_tuple_name(n):
	names = {1: 'single', 2: 'pair', 3: 'triple', 4: 'quad'}
	return names.get(n, '%d-tuple' % n)

def any_equal(s):
	return len(set(s)) < len(s)

def all_equal(s):
	return all(all(x == y for y in s) for x in s)

def union(s):
	return set().union(*s)

def intersection(s):
	s = list(s)
	return set(s[0]).intersection(*s)

class Color(object):
	
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
	
	def colored(self, s):
		return '\x1b[%sm%s\x1b[0m' % (self.code, s)

Color.NEITHER = Color(0, 'neither', '0')
Color.RED = Color(1, 'red', '31;1')
Color.BLUE = Color(~1, 'blue', '44')

class Cell(object):
	
	VALUES = range(1, 10)
	ROWS = 'ABCDEFGHJ'
	COLS = '123456789'
	BLOCKS = '123456789'
	
	def __init__(self, x, y, ds=None):
		self.x = x
		self.y = y
		self.b = y // 3 * 3 + x // 3
		if type(ds) in [list, tuple, set]:
			self.ds = set(ds)
		elif ds in Cell.VALUES or ds in map(str, Cell.VALUES):
			self.ds = {int(ds)}
		else:
			self.ds = set(Cell.VALUES)
		self.dcs = {}
	
	def __str__(self):
		return '%s = {%s}' % (self.cell_name(), ', '.join(
			self.dcs.get(d, Color.NEITHER).colored(d) for d in sorted(self.ds)))
	
	def __repr__(self):
		return 'Cell(%d, %d, {%s})' % (self.x, self.y, ', '.join(
			self.dcs.get(d, Color.NEITHER).colored(d) for d in sorted(self.ds)))
	
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
		n = len(self.ds)
		self.ds -= set(ds)
		return len(self.ds) < n
	
	def include_only(self, ds):
		n = len(self.ds)
		self.ds &= set(ds)
		return len(self.ds) < n

class Sudoku(object):
	
	UNIT_TYPES = ['row', 'column', 'block']
	
	def __init__(self, *cells):
		if len(cells) == 1:
			cells = cells[0]
			if isinstance(cells, str):
				cells = filter(None, (c if c in '123456789' else
					'0' if c in '0._*' else '' for c in cells))
			cells = list(cells)
		if len(cells) == 9:
			cells = flatten(map(list, cells))
		if len(cells) != 81:
			raise ValueError('Invalid Sudoku board')
		self.cm = []
		while cells:
			row, cells = cells[:9], cells[9:]
			row = [Cell(i, len(self.cm), d) for i, d in enumerate(row)]
			self.cm.append(row)
	
	def __repr__(self):
		return 'Sudoku(%r)' % ''.join(str(c.value()) for c in self.cells())
	
	def __str__(self):
		return self._solved_str() if self.solved() else self._unsolved_str()
	
	def _solved_str(self):
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
	
	def _unsolved_str(self):
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
			'column': self.column_without,
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
	
	def solve_strip_naked_singles(self, verbose=False):
		if self.solved():
			return False
		if verbose:
			print('Eliminate candidate values to find naked singles')
		changed = False
		for y, x in product(range(9), range(9)):
			changed |= self.solve_strip_naked_single(x, y, verbose)
		if verbose and not changed:
			print('...No naked singles found')
		return changed
	
	def solve_strip_naked_single(self, x, y, verbose=False):
		cell = self.cell(x, y)
		if cell.solved():
			return False
		seen_values = {c.value() for c in self.seen_from(x, y)}
		changed = cell.exclude(seen_values)
		if verbose and changed:
			print(' * Cell %s can only be %s' % (cell.cell_name(),
				cell.value_string()))
		return changed
	
	def solve_naked_n_tuples(self, n, verbose=False):
		if self.solved():
			return False
		tuple_name = n_tuple_name(n)
		if verbose:
			print('Observe candidate values to find naked %ss' % tuple_name)
		changed = False
		for unit_type, i in product(Sudoku.UNIT_TYPES, range(9)):
			changed |= self.solve_naked_n_tuples_in_unit(unit_type, n, i, verbose)
		if verbose and not changed:
			print('...No naked %ss found' % tuple_name)
		return changed
	
	def solve_naked_n_tuples_in_unit(self, unit_type, n, i, verbose=False):
		changed = False
		unit = self.unit(unit_type, i)
		filtered_unit = [c for c in unit if len(c.ds) in range(2, n+1)]
		for cells in combinations(filtered_unit, n):
			if not all_equal(c.ds for c in cells):
				continue
			sample_cell = cells[0]
			candidates = sample_cell.ds
			unit_changed = False
			for cell in unit:
				if cell in cells:
					continue
				unit_changed |= cell.exclude(candidates)
			changed |= unit_changed
			if verbose and unit_changed:
				print(' * In %s %s, cells (%s) can only be %s' %
					(unit_type, self.unit_name(unit_type, i),
						', '.join(c.cell_name() for c in cells),
						set_string(candidates)))
		return changed
	
	def solve_hidden_n_tuples(self, n, verbose=False):
		if self.solved():
			return False
		tuple_name = n_tuple_name(n)
		if verbose:
			print('Observe candidate values to find hidden %ss' % tuple_name)
		changed = False
		for unit_type, i in product(Sudoku.UNIT_TYPES, range(9)):
			changed |= self.solve_hidden_n_tuples_in_unit(unit_type, n, i, verbose)
		if verbose and not changed:
			print('...No hidden %ss found' % tuple_name)
		return changed
	
	def solve_hidden_n_tuples_in_unit(self, unit_type, n, i, verbose=False):
		changed = False
		unit = self.unit(unit_type, i)
		filtered_unit = [c for c in unit if not c.solved()]
		for cells in combinations(filtered_unit, n):
			cells_candidates = union(c.ds for c in cells)
			unit_candidates = union(c.ds for c in set(self.unit(unit_type, i)) - set(cells))
			n_tuple_uniques = cells_candidates - unit_candidates
			if len(n_tuple_uniques) != n:
				continue
			subset_changed = False
			for cell in cells:
				subset_changed |= cell.include_only(n_tuple_uniques)
			changed |= subset_changed
			if verbose and subset_changed:
				if n == 1:
					cell = cells[0]
					print(' * In %s %s, only cell %s can be %s' %
						(unit_type, self.unit_name(unit_type, i),
							cell.cell_name(), cell.value()))
				else:
					print(' * In %s %s, only cells (%s) can be %s' %
						(unit_type, self.unit_name(unit_type, i),
							', '.join(c.cell_name() for c in cells),
							set_string(n_tuple_uniques)))
		return changed
	
	def solve_unit_intersection_removals(self, unit_type, verbose=False):
		if self.solved():
			return False
		intersection_plurals = {
			'row': "block+row reductions",
			'column': "block+column reductions",
			'block': 'pointing pairs/triples'}
		intersection_plural = intersection_plurals[unit_type]
		if verbose:
			print('Observe candidate values to find %s' % intersection_plural)
		changed = False
		for i in range(9):
			num_solved = self.num_solved()
			changed |= self.solve_unit_intersection_removals_in_unit(unit_type, i, verbose)
			if self.num_solved() > num_solved:
				return True
		if verbose and not changed:
			print('...No %s found' % intersection_plural)
		return changed
	
	def solve_unit_intersection_removals_in_unit(self, unit_type, i, verbose=False):
		changed = False
		unit = self.unit(unit_type, i)
		for d in Cell.VALUES:
			filtered_unit = [c for c in unit if not c.solved() and d in c.ds]
			if not filtered_unit:
				continue
			sample_cell = filtered_unit[0]
			intersection = intersection_type = None
			if all_equal(c.y for c in filtered_unit) and unit_type != 'row':
				intersection = self.row(sample_cell.y)
				intersection_type = 'row'
			elif all_equal(c.x for c in filtered_unit) and unit_type != 'column':
				intersection = self.col(sample_cell.x)
				intersection_type = 'column'
			elif all_equal(c.b for c in filtered_unit) and unit_type != 'block':
				intersection = self.block(sample_cell.b)
				intersection_type = 'block'
			if not intersection:
				continue
			intersection_changed = False
			intersection_solved = []
			for cell in intersection:
				if cell in unit:
					continue
				cell_changed = cell.exclude({d})
				if cell_changed and cell.solved():
					intersection_solved.append(cell)
				intersection_changed |= cell_changed
			changed |= intersection_changed
			if verbose and intersection_changed:
				print(' * In %s %s, only a %s in %s %s can be %d' %
					(unit_type, self.unit_name(unit_type, i),
						n_tuple_name(len(filtered_unit)), intersection_type,
						sample_cell.unit_name(intersection_type), d))
				for cell in intersection_solved:
					print('    > Cell %s can only be %s' %
						(cell.cell_name(), cell.value()))
		return changed
	
	def solve_n_fish(self, n, verbose=False):
		if self.solved():
			return False
		n_fish_name = {2: 'X-wing', 3: 'swordfish', 4: 'jellyfish'}[n]
		if verbose:
			print('Observe candidate values to find %s patterns' % n_fish_name)
		changed = False
		for unit_type, indexes in product(['row', 'column'], combinations(range(9), n)):
			num_solved = self.num_solved()
			changed |= self.solve_n_fish_in_units(unit_type, n, indexes, verbose)
			if self.num_solved() > num_solved:
				return True
		if verbose and not changed:
			print('...No %s patterns found' % n_fish_name)
		return changed
	
	def solve_n_fish_in_units(self, unit_type, n, indexes, verbose=False):
		changed = False
		units = [self.unit(unit_type, i) for i in indexes]
		for d in Cell.VALUES:
			filtered_units = [c for u in units for c in u if not c.solved() and d in c.ds]
			other_indexes = []
			if unit_type == 'row':
				if len({c.y for c in filtered_units}) != n:
					continue
				other_unit_type = 'column'
				other_indexes = {c.x for c in filtered_units}
			elif unit_type == 'column':
				if len({c.x for c in filtered_units}) != n:
					continue
				other_unit_type = 'row'
				other_indexes = {c.y for c in filtered_units}
			if len(other_indexes) != n:
				continue
			n_fish_changed = False
			n_fish_solved = []
			for i in other_indexes:
				other_unit = self.unit(other_unit_type, i)
				for cell in other_unit:
					if cell in filtered_units:
						continue
					cell_changed = cell.exclude({d})
					if cell_changed and cell.solved():
						n_fish_solved.append(cell)
					n_fish_changed |= cell_changed
			changed |= n_fish_changed
			if verbose and n_fish_changed:
				print(' * In %ss (%s), %d can only be in %ss (%s)' %
					(other_unit_type, ', '.join(self.unit_name(other_unit_type, i)
							for i in sorted(other_indexes)),
						d, unit_type, ', '.join(self.unit_name(unit_type, i)
							for i in sorted(indexes))))
				for cell in n_fish_solved:
					print('    > Cell %s can only be %s' %
						(cell.cell_name(), cell.value()))
		return changed
	
	def solve_3d_medusas(self, verbose=False):
		if self.solved():
			return False
		if verbose:
			print('Color chains of candidate values (3D Medusas) to eliminate candidates')
		changed = False
		for y, x in product(range(9), range(9)):
			num_solved = self.num_solved()
			changed |= self.solve_3d_medusas_from(x, y, verbose)
			if self.num_solved() > num_solved:
				return True
		if verbose and not changed:
			print('...No 3D Medusas found')
		return changed
	
	def solve_3d_medusas_from(self, x, y, verbose=False):
		start_cell = self.cell(x, y)
		if not start_cell.bi_value():
			return False
		p, q = sorted(start_cell.ds)
		start_cell.dcs[p], start_cell.dcs[q] = Color.RED, Color.BLUE
		while (self._3d_medusa_color_bi_value_cells(verbose) or
			self._3d_medusa_color_bi_location_units(verbose)):
			pass
		changed = (self._3d_medusa_rule_1(start_cell, verbose) or
			self._3d_medusa_rule_2(start_cell, verbose) or
			self._3d_medusa_rule_3(start_cell, verbose) or
			self._3d_medusa_rule_4(start_cell, verbose) or
			self._3d_medusa_rule_5(start_cell, verbose) or
			self._3d_medusa_rule_6(start_cell, verbose))
		for cell in self.cells():
			cell.dcs = {}
		return changed
	
	def _3d_medusa_color_bi_value_cells(self, verbose=False):
		colored = False
		for cell in self.cells():
			if not cell.bi_value() or len(cell.dcs) != 1:
				continue
			d_colored, d_uncolored = cell.ds
			if d_uncolored in cell.dcs:
				d_colored, d_uncolored = d_uncolored, d_colored
			cell.dcs[d_uncolored] = ~cell.dcs[d_colored]
			colored = True
		return colored
	
	def _3d_medusa_color_bi_location_units(self, verbose=False):
		colored = False
		for unit_type, i in product(Sudoku.UNIT_TYPES, range(9)):
			unit = self.unit(unit_type, i)
			unsolved_ds = union(c.ds for c in unit if not c.solved())
			for d in unsolved_ds:
				filtered_unit = [c for c in unit if not c.solved() and d in c.ds]
				if len(filtered_unit) != 2:
					continue
				cell_colored, cell_uncolored = filtered_unit
				if d not in cell_colored.dcs:
					cell_colored, cell_uncolored = cell_uncolored, cell_colored
				if d in cell_uncolored.dcs or d not in cell_colored.dcs:
					continue
				cell_uncolored.dcs[d] = ~cell_colored.dcs[d]
				colored = True
		return colored
	
	def _3d_medusa_rule_1(self, start_cell, verbose=False):
		for cell in self.cells():
			colors = cell.dcs.values()
			dup_color = None
			if colors.count(Color.RED) > 1:
				dup_color = Color.RED
			elif colors.count(Color.BLUE) > 1:
				dup_color = Color.BLUE
			else:
				continue
			if verbose:
				self._3d_medusa_print_chain_start(start_cell)
				print(' > Find a cell with multiple candidates in the same color')
				dup_candidates = {d for d in cell.dcs if cell.dcs[d] == dup_color}
				print(' > Cell %s has multiple candidates %s colored %s' %
					(cell.cell_name(), set_string(dup_candidates), dup_color))
			return self._3d_medusa_eliminate_color(dup_color, verbose)
		return False
	
	def _3d_medusa_rule_2(self, start_cell, verbose=False):
		for unit_type, i, d in product(Sudoku.UNIT_TYPES, range(9), Cell.VALUES):
			unit = self.unit(unit_type, i)
			colors = [c.dcs[d] for c in unit if d in c.dcs]
			dup_color = Color.NEITHER
			if colors.count(Color.RED) > 1:
				dup_color = Color.RED
			elif colors.count(Color.BLUE) > 1:
				dup_color = Color.BLUE
			else:
				continue
			if verbose:
				self._3d_medusa_print_chain_start(start_cell)
				print(' > Find a unit with multiple cells with the same candidate in the same color')
				dup_cell_names = [c.cell_name() for c in unit
					if c.dcs.get(d, Color.NEITHER) == dup_color]
				print(' > %s %s has multiple cells (%s) with candidate %d colored %s' %
					(unit_type.capitalize(), self.unit_name(unit_type, i),
						', '.join(dup_cell_names), d, dup_color))
			return self._3d_medusa_eliminate_color(dup_color, verbose)
		return False
	
	def _3d_medusa_rule_3(self, start_cell, verbose=False):
		changed = False
		for cell in self.cells():
			if len(set(cell.dcs.values())) != 2:
				continue
			cell_changed = cell.include_only(cell.dcs.keys())
			if verbose and cell_changed:
				if not changed:
					self._3d_medusa_print_chain_start(start_cell)
					print(' > Find cells with candidates in both colors and others uncolored')
				p, q = sorted(cell.dcs)
				print(' * Cell %s can only be %s, since %d is colored %s and %d is %s' %
					(cell.cell_name(), cell.value_string(), p, cell.dcs[p],
						q, cell.dcs[q]))
			changed |= cell_changed
		return changed
	
	def _3d_medusa_rule_4(self, start_cell, verbose=False):
		changed = False
		for cell in self.cells():
			if cell.solved():
				continue
			seen = self.seen_from(cell.x, cell.y)
			for d in cell.ds - set(cell.dcs):
				d_colors = {c.dcs[d] for c in seen if d in c.dcs}
				if len(d_colors) != 2:
					continue
				cell_changed = cell.exclude({d})
				if verbose and cell_changed:
					if not changed:
						self._3d_medusa_print_chain_start(start_cell)
						print(' > Find cells with an uncolored candidate that can be seen in both colors')
					print(' * Cell %s can only be %s, since it can see %d in both colors' %
						(cell.cell_name(), cell.value_string(), d))
				changed |= cell_changed
		return changed
	
	def _3d_medusa_rule_5(self, start_cell, verbose=False):
		changed = False
		for cell in self.cells():
			if len(cell.dcs) != 1:
				continue
			d_colored = cell.dcs.keys()[0]
			d_color = cell.dcs[d_colored]
			seen = self.seen_from(cell.x, cell.y)
			for d in cell.ds - {d_colored}:
				if not any(c for c in seen if c.dcs.get(d, Color.NEITHER) == ~d_color):
					continue
				cell_changed = cell.exclude({d})
				if verbose and cell_changed:
					if not changed:
						self._3d_medusa_print_chain_start(start_cell)
						print(' > Find cells with a candidate in one color that can see it in the other color')
					print(' * Cell %s can only be %s, since its %d is %s and it can see %d in %s' %
						(cell.cell_name(), cell.value_string(), d_colored,
							d_color, d, ~d_color))
				changed |= cell_changed
		return changed
	
	def _3d_medusa_rule_6(self, start_cell, verbose=False):
		for cell in self.cells():
			if cell.dcs:
				continue
			seen = self.seen_from(cell.x, cell.y)
			seen_colors = {d: {c.dcs[d] for c in seen if d in c.dcs} for d in cell.ds}
			seen_color = None
			if all(Color.RED in seen_colors[d] for d in cell.ds):
				seen_color = Color.RED
			elif all(Color.BLUE in seen_colors[d] for d in cell.ds):
				seen_color = Color.BLUE
			else:
				continue
			if verbose:
				self._3d_medusa_print_chain_start(start_cell)
				print(' > Find cells that can see all their candidates in the same color')
				print(' * Cell %s can see all its candidates %s in %s' %
					(cell.cell_name(), cell.value_string(), seen_color))
			return self._3d_medusa_eliminate_color(seen_color, verbose)
		return False
	
	def _3d_medusa_print_chain_start(self, start_cell):
		p, q = sorted(start_cell.ds)
		print(' > Start chains from cell %s, coloring %d %s and %d %s' %
			(start_cell.cell_name(), p, start_cell.dcs[p], q, start_cell.dcs[q]))
	
	def _3d_medusa_eliminate_color(self, color, verbose=False):
		if verbose:
			print(' > Eliminate all candidates colored %s' % color)
		changed = False
		for cell in self.cells():
			for d in cell.dcs:
				if cell.dcs[d] != color:
					continue
				changed |= cell.exclude({d})
				if verbose:
					print(' * Cell %s can only be %s' % (cell.cell_name(),
						cell.value_string()))
		return changed
	
	def solve_n_cell_subset_exclusion(self, n, verbose=False):
		if self.solved():
			return False
		if verbose:
			print('Examine subsets of %d unsolved cells to eliminate candidates' % n)
		unsolved_cells = [c for c in self.cells() if not c.solved()]
		for subset in combinations(unsolved_cells, n):
			seen = intersection(self.seen_from(c.x, c.y) for c in subset)
			# TODO: remove impossible assignments that assign the same value to
			# cells in the subset that can see each other
			assignments = [a for a in product(*[c.ds for c in subset])
				if not any(c.ds.issubset(a) for c in seen)]
			for cell, ds in zip(subset, transpose(assignments)):
				if not cell.include_only(ds):
					continue
				if verbose:
					print(' * Cell %s of (%s) can only be %s' % (cell.cell_name(),
						', '.join(c.cell_name() for c in subset),
						cell.value_string()))
				return True
		if verbose:
			print('...No %d-cell subset exclusions found' % n)
		return False

	def solve_methods(self, verbose=False):
		if self.solved():
			return False
		if self.solve_strip_naked_singles(verbose):
			return True
		if self.solve_hidden_n_tuples(1, verbose):
			return True
		for n in range(2, 5):
			if self.solve_naked_n_tuples(n, verbose):
				return True
			if self.solve_hidden_n_tuples(n, verbose):
				return True
		for unit_type in Sudoku.UNIT_TYPES:
			if self.solve_unit_intersection_removals(unit_type, verbose):
				return True
		for n in range(2, 5):
			if self.solve_n_fish(n, verbose):
				return True
		if self.solve_3d_medusas(verbose):
			return True
		for n in range(2, 4): # larger subsets are too slow
			if self.solve_n_cell_subset_exclusion(n, verbose):
				return True
		return False
	
	def solve(self, verbose=False):
		if self.solved():
			if verbose:
				print('Already solved!')
			return True
		if verbose:
			print('Solving %r' % self)
		num_solved = self.num_solved()
		while self.solve_methods(verbose):
			pass
		if verbose:
			if self.solved():
				print('Completely solved!')
			else:
				print('...Cannot solve further (solved %d cells)' %
					(self.num_solved() - num_solved))
		return self.solved()
