from __future__ import print_function

from utils import *
from color import *
from cell import *
from board import *

from itertools import product, combinations

@Sudoku.strategy('naked singles', 1)
def solve_strip_naked_singles(sudoku, verbose):
	"""Exclude the values of seen solved cells as candidates for unsolved cells."""
	return any([solve_strip_naked_single(sudoku, x, y, verbose)
		for y, x in product(range(9), range(9))])

def solve_strip_naked_single(sudoku, x, y, verbose):
	cell = sudoku.cell(x, y)
	if cell.solved():
		return False
	seen_values = {c.value() for c in sudoku.seen_from(x, y)}
	changed = cell.exclude(seen_values)
	if verbose and changed:
		print(' * Cell %s can only be %s' % (cell.cell_name(),
			cell.value_string()))
	return changed

@Sudoku.strategy('naked pairs', 3)
def solve_naked_pairs(sudoku, verbose):
	"""Exclude the candidates of seen bi-value cell pairs from unsolved cells
	in their unit."""
	return solve_naked_n_tuples(sudoku, 2, verbose)

@Sudoku.strategy('naked triples', 5)
def solve_naked_triples(sudoku, verbose):
	"""Exclude the candidates of seen tri-value cell triples from unsolved cells
	in their unit."""
	return solve_naked_n_tuples(sudoku, 3, verbose)

@Sudoku.strategy('naked quads', 7)
def solve_naked_quads(sudoku, verbose):
	"""Exclude the candidates of seen quad-value cell quads from unsolved cells
	in their unit."""
	return solve_naked_n_tuples(sudoku, 4, verbose)

def solve_naked_n_tuples(sudoku, n, verbose):
	return any([solve_naked_n_tuples_in_unit(sudoku, unit_type, n, i, verbose)
		for unit_type, i in product(Sudoku.UNIT_TYPES, range(9))])

def solve_naked_n_tuples_in_unit(sudoku, unit_type, n, i, verbose):
	changed = False
	unit = sudoku.unit(unit_type, i)
	filtered_unit = [c for c in unit if len(c.ds) in range(2, n+1)]
	for cells in combinations(filtered_unit, n):
		candidates = union(c.ds for c in cells)
		if len(candidates) != n:
			continue
		unit_changed = False
		for cell in unit:
			if cell in cells:
				continue
			unit_changed |= cell.exclude(candidates)
		changed |= unit_changed
		if verbose and unit_changed:
			print(' * In %s %s, cells (%s) can only be %s' %
				(unit_type, sudoku.unit_name(unit_type, i),
					', '.join(c.cell_name() for c in cells),
					set_string(candidates)))
	return changed

@Sudoku.strategy('hidden singles', 2)
def solve_hidden_singles(sudoku, verbose):
	"""Find cells with a unique candidate in a unit and set them to that value."""
	return solve_hidden_n_tuples(sudoku, 1, verbose)

@Sudoku.strategy('hidden pairs', 4)
def solve_hidden_pairs(sudoku, verbose):
	"""Find pairs of cells with two unique candidates in a unit and limit them
	to those candidates."""
	return solve_hidden_n_tuples(sudoku, 2, verbose)

@Sudoku.strategy('hidden triples', 6)
def solve_hidden_triples(sudoku, verbose):
	"""Find triples of cells with three unique candidates in a unit and limit them
	to those candidates."""
	return solve_hidden_n_tuples(sudoku, 3, verbose)

@Sudoku.strategy('hidden quads', 8)
def solve_hidden_quads(sudoku, verbose):
	"""Find quads of cells with four unique candidates in a unit and limit them
	to those candidates."""
	return solve_hidden_n_tuples(sudoku, 4, verbose)

def solve_hidden_n_tuples(sudoku, n, verbose):
	return any([solve_hidden_n_tuples_in_unit(sudoku, unit_type, n, i, verbose)
		for unit_type, i in product(Sudoku.UNIT_TYPES, range(9))])

def solve_hidden_n_tuples_in_unit(sudoku, unit_type, n, i, verbose):
	changed = False
	unit = sudoku.unit(unit_type, i)
	filtered_unit = [c for c in unit if not c.solved()]
	for cells in combinations(filtered_unit, n):
		cells_candidates = union(c.ds for c in cells)
		unit_candidates = union(c.ds for c in set(sudoku.unit(unit_type, i)) - set(cells))
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
					(unit_type, sudoku.unit_name(unit_type, i),
						cell.cell_name(), cell.value()))
			else:
				print(' * In %s %s, only cells (%s) can be %s' %
					(unit_type, sudoku.unit_name(unit_type, i),
						', '.join(c.cell_name() for c in cells),
						set_string(n_tuple_uniques)))
	return changed

@Sudoku.strategy('unit intersection', 9)
def solve_unit_intersections(sudoku, verbose):
	"""Find pairs/triples of cells in a unit with a unique candidate, that are
	also all in one intersecting unit, and exclude that candidate from the
	other cells in the intersecting unit."""
	return any(solve_unit_intersections_in_unit(sudoku, unit_type, i, verbose)
		for unit_type, i in product(Sudoku.UNIT_TYPES, range(9)))

def solve_unit_intersections_in_unit(sudoku, unit_type, i, verbose):
	changed = False
	unit = sudoku.unit(unit_type, i)
	for d in Cell.VALUES:
		filtered_unit = [c for c in unit if not c.solved() and d in c.ds]
		if not filtered_unit:
			continue
		sample_cell = filtered_unit[0]
		intersection = intersection_type = None
		if all_equal(c.y for c in filtered_unit) and unit_type != 'row':
			intersection = sudoku.row(sample_cell.y)
			intersection_type = 'row'
		elif all_equal(c.x for c in filtered_unit) and unit_type != 'column':
			intersection = sudoku.col(sample_cell.x)
			intersection_type = 'column'
		elif all_equal(c.b for c in filtered_unit) and unit_type != 'block':
			intersection = sudoku.block(sample_cell.b)
			intersection_type = 'block'
		if not intersection:
			continue
		intersection_changed = False
		intersection_changed_cells = []
		for cell in intersection:
			if cell in unit:
				continue
			cell_changed = cell.exclude({d})
			if cell_changed:
				intersection_changed_cells.append(cell)
			intersection_changed |= cell_changed
		changed |= intersection_changed
		if verbose and intersection_changed:
			print(' * In %s %s, only a %s in %s %s can be %d' %
				(unit_type, sudoku.unit_name(unit_type, i),
					n_tuple_name(len(filtered_unit)), intersection_type,
					sample_cell.unit_name(intersection_type), d))
			for cell in intersection_changed_cells:
				print('    > Cell %s can only be %s' %
					(cell.cell_name(), cell.value_string()))
	return changed

@Sudoku.strategy('X-wing', 10)
def solve_x_wings(sudoku, verbose):
	"""Find two pairs of cells with a unique candidate in two different units,
	that are also both in two intersecting units, and exclude that candidate
	from the other cells in the intersecting units."""
	return solve_n_fish(sudoku, 2, verbose)

@Sudoku.strategy('swordfish', 12)
def solve_swordfish(sudoku, verbose):
	"""Find three triples of cells with a unique candidate in three different
	units, that are also both in three intersecting units, and exclude that
	candidate from the other cells in the intersecting units."""
	return solve_n_fish(sudoku, 3, verbose)

@Sudoku.strategy('jellyfish', 16)
def solve_jellyfish(sudoku, verbose):
	"""Find four quads of cells with a unique candidate in four different units,
	that are also both in four intersecting units, and exclude that candidate
	from the other cells in the intersecting units."""
	return solve_n_fish(sudoku, 4, verbose)

def solve_n_fish(sudoku, n, verbose):
	return any(solve_n_fish_in_units(sudoku, unit_type, n, indexes, verbose)
		for unit_type, indexes in product(['row', 'column'], combinations(range(9), n)))

def solve_n_fish_in_units(sudoku, unit_type, n, indexes, verbose):
	changed = False
	units = [sudoku.unit(unit_type, i) for i in indexes]
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
			other_unit = sudoku.unit(other_unit_type, i)
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
				(other_unit_type, ', '.join(sudoku.unit_name(other_unit_type, i)
						for i in sorted(other_indexes)),
					d, unit_type, ', '.join(sudoku.unit_name(unit_type, i)
						for i in sorted(indexes))))
			for cell in n_fish_solved:
				print('    > Cell %s can only be %s' %
					(cell.cell_name(), cell.value()))
	return changed

@Sudoku.strategy('Y-wing', 11)
def solve_y_wings(sudoku, verbose):
	"""Find a "hinge" cell with candidates {X, Y}, that can see two "wing" cells
	with candidates {X, Z} and {Y, Z}, such that the wings cannot see each other;
	and exclude Z from any cells that can see both wings."""
	return any(solve_y_wing_from(sudoku, x, y, verbose)
		for y, x in product(range(9), range(9)))

def solve_y_wing_from(sudoku, x, y, verbose):
	hinge = sudoku.cell(x, y)
	if not hinge.bi_value():
		return False
	p, q = sorted(hinge.ds)
	seen = sudoku.seen_from(hinge.x, hinge.y)
	for r in Cell.VALUES:
		if r in [p, q]:
			continue
		wing1s = [c for c in seen if c.ds == {p, r}]
		wing2s = [c for c in seen if c.ds == {q, r}]
		for wing1, wing2 in product(wing1s, wing2s):
			cells = sudoku.seen_from(wing1.x, wing1.y)
			if wing2 in cells:
				continue
			cells &= sudoku.seen_from(wing2.x, wing2.y)
			cells = [c for c in cells if not c.solved() and r in c.ds]
			if not cells:
				continue
			if verbose:
				print(' - Y-wing with hinge at cell %s %s and wings at %s %s and %s %s' %
					(hinge.cell_name(), hinge.value_string(), wing1.cell_name(),
					wing1.value_string(), wing2.cell_name(), wing2.value_string()))
			for cell in cells:
				cell.exclude({r})
				if verbose:
					print('    > Cell %s can only be %s' %
						(cell.cell_name(), cell.value_string()))
			return True
	return False

@Sudoku.strategy('XYZ-wing', 13)
def solve_xyz_wings(sudoku, verbose):
	"""Find a "hinge" cell with candidates {X, Y, Z}, that can see two "wing"
	cells with candidates {X, Z} and {Y, Z}, such that the wings cannot see each
	other; and exclude Z from any cells that can see both wings and the hinge."""
	return any(solve_xyz_wing_from(sudoku, x, y, verbose)
		for y, x in product(range(9), range(9)))

def solve_xyz_wing_from(sudoku, x, y, verbose):
	hinge = sudoku.cell(x, y)
	if len(hinge.ds) != 3:
		return False
	seen = sudoku.seen_from(hinge.x, hinge.y)
	for r in sorted(hinge.ds):
		p, q = sorted(hinge.ds - {r})
		wing1s = [c for c in seen if c.ds == {p, r}]
		wing2s = [c for c in seen if c.ds == {q, r}]
		for wing1, wing2 in product(wing1s, wing2s):
			cells = sudoku.seen_from(wing1.x, wing1.y)
			if wing2 in cells:
				continue
			cells &= sudoku.seen_from(wing2.x, wing2.y)
			cells &= sudoku.seen_from(hinge.x, hinge.y)
			cells = [c for c in cells if not c.solved() and r in c.ds]
			if not cells:
				continue
			if verbose:
				print(' - XYZ-wing with hinge at cell %s %s and wings at %s %s and %s %s' %
					(hinge.cell_name(), hinge.value_string(), wing1.cell_name(),
					wing1.value_string(), wing2.cell_name(), wing2.value_string()))
			for cell in cells:
				cell.exclude({r})
				if verbose:
					print('    > Cell %s can only be %s' %
						(cell.cell_name(), cell.value_string()))
			return True
	return False

@Sudoku.strategy('3D Medusa', 14)
def solve_3d_medusas(sudoku, verbose):
	"""Color two candidates of a bi-value cell red and blue, and propagate the
	colors outward along strong links; then infer the correct color based on the
	derived contradictions or tautologies."""
	return any(solve_3d_medusas_from(sudoku, x, y, verbose)
		for y, x in product(range(9), range(9)))

def solve_3d_medusas_from(sudoku, x, y, verbose):
	start_cell = sudoku.cell(x, y)
	if not start_cell.bi_value():
		return False
	p, q = sorted(start_cell.ds)
	start_cell.dcs[p], start_cell.dcs[q] = Color.RED, Color.BLUE
	while (medusa_color_bi_value_cells(sudoku, verbose) or
		medusa_color_bi_location_units(sudoku, verbose)):
		pass
	print_start = lambda: (m3d_medusa_print_chain_start(sudoku, start_cell), print(sudoku))
	changed = (medusa_check_cell_contradictions(sudoku, print_start, verbose) or
		medusa_check_unit_contradictions(sudoku, print_start, verbose) or
		medusa_check_seen_contradictions(sudoku, print_start, verbose))
	if not changed:
		changed |= medusa_check_full_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= medusa_check_emptied_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= medusa_check_partial_cells(sudoku, print_start, verbose)
	for cell in sudoku.cells():
		cell.dcs = {}
	return changed

def m3d_medusa_print_chain_start(sudoku, start_cell):
	p, q = sorted(start_cell.ds)
	print(' - Start chains from cell %s, coloring %d %s and %d %s' %
		(start_cell.cell_name(), p, start_cell.dcs[p], q, start_cell.dcs[q]))

@Sudoku.strategy('dual Medusa', 15)
def solve_dual_medusas(sudoku, verbose):
	"""Color two bi-location candidates in a unit red and blue, and propagate
	the colors outward along strong links; then infer the correct color based on
	the derived contradictions or tautologies."""
	return any(solve_dual_medusas_from(sudoku, unit_type, i, d, verbose)
		for unit_type, i, d in product(Sudoku.UNIT_TYPES, range(9), Cell.VALUES))

def solve_dual_medusas_from(sudoku, unit_type, i, d, verbose):
	unit = sudoku.unit(unit_type, i)
	start_cells = [c for c in unit if d in c.ds]
	if len(start_cells) != 2:
		return False
	start_red, start_blue = sorted(start_cells)
	start_red.dcs[d], start_blue.dcs[d] = Color.RED, Color.BLUE
	while (medusa_color_bi_value_cells(sudoku, verbose) or
		medusa_color_bi_location_units(sudoku, verbose)):
		pass
	print_start = lambda: (dual_medusa_print_chain_start(sudoku, unit_type, i, d), print(sudoku))
	changed = (medusa_check_cell_contradictions(sudoku, print_start, verbose) or
		medusa_check_unit_contradictions(sudoku, print_start, verbose) or
		medusa_check_seen_contradictions(sudoku, print_start, verbose))
	if not changed:
		changed |= medusa_check_full_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= medusa_check_emptied_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= medusa_check_partial_cells(sudoku, print_start, verbose)
	for cell in sudoku.cells():
		cell.dcs = {}
	return changed

def dual_medusa_print_chain_start(sudoku, unit_type, i, d):
	unit = sudoku.unit(unit_type, i)
	start_cells = [c for c in unit if d in c.ds]
	start_red, start_blue = sorted(start_cells)
	print(' - Start from %s %s, coloring %d %s in cell %s and %s in cell %s' %
		(unit_type, sudoku.unit_name(unit_type, i), d, start_red.dcs[d],
			start_red.cell_name(), start_blue.dcs[d], start_blue.cell_name()))

def medusa_color_bi_value_cells(sudoku, verbose):
	colored = False
	for cell in sudoku.cells():
		if not cell.bi_value() or len(cell.dcs) != 1:
			continue
		d_colored, d_uncolored = cell.ds
		if d_uncolored in cell.dcs:
			d_colored, d_uncolored = d_uncolored, d_colored
		cell.dcs[d_uncolored] = ~cell.dcs[d_colored]
		colored = True
	return colored

def medusa_color_bi_location_units(sudoku, verbose):
	colored = False
	for unit_type, i in product(Sudoku.UNIT_TYPES, range(9)):
		unit = sudoku.unit(unit_type, i)
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

def medusa_check_cell_contradictions(sudoku, print_start, verbose):
	for cell in sudoku.cells():
		colors = cell.dcs.values()
		dup_color = None
		if colors.count(Color.RED) > 1:
			dup_color = Color.RED
		elif colors.count(Color.BLUE) > 1:
			dup_color = Color.BLUE
		else:
			continue
		if verbose:
			print_start()
			print(' - Find a cell with multiple candidates in the same color')
			dup_candidates = {d for d in cell.dcs if cell.dcs[d] == dup_color}
			print(' - Cell %s has multiple candidates %s colored %s' %
				(cell.cell_name(), set_string(dup_candidates), dup_color))
		return medusa_eliminate_color(sudoku, dup_color, verbose)
	return False

def medusa_check_unit_contradictions(sudoku, print_start, verbose):
	for unit_type, i, d in product(Sudoku.UNIT_TYPES, range(9), Cell.VALUES):
		unit = sudoku.unit(unit_type, i)
		colors = [c.dcs[d] for c in unit if d in c.dcs]
		dup_color = Color.NEITHER
		if colors.count(Color.RED) > 1:
			dup_color = Color.RED
		elif colors.count(Color.BLUE) > 1:
			dup_color = Color.BLUE
		else:
			continue
		if verbose:
			print_start()
			print(' - Find a unit with multiple cells with the same candidate in the same color')
			dup_cell_names = [c.cell_name() for c in unit
				if c.dcs.get(d, Color.NEITHER) == dup_color]
			print(' - %s %s has multiple cells (%s) with candidate %d colored %s' %
				(unit_type.capitalize(), sudoku.unit_name(unit_type, i),
					', '.join(dup_cell_names), d, dup_color))
		return medusa_eliminate_color(sudoku, dup_color, verbose)
	return False

def medusa_check_seen_contradictions(sudoku, print_start, verbose):
	for cell in sudoku.cells():
		if cell.dcs:
			continue
		seen = sudoku.seen_from(cell.x, cell.y)
		seen_colors = {d: {c.dcs[d] for c in seen if d in c.dcs} for d in cell.ds}
		seen_color = None
		if all(Color.RED in seen_colors[d] for d in cell.ds):
			seen_color = Color.RED
		elif all(Color.BLUE in seen_colors[d] for d in cell.ds):
			seen_color = Color.BLUE
		else:
			continue
		if verbose:
			print_start()
			print(' - Find cells that can see all their candidates in the same color')
			print(' * Cell %s can see all its candidates %s in %s' %
				(cell.cell_name(), cell.value_string(), seen_color))
		return medusa_eliminate_color(sudoku, seen_color, verbose)
	return False

def medusa_eliminate_color(sudoku, color, verbose):
	if verbose:
		print(' - Eliminate all candidates colored %s' % color)
	changed = False
	for cell in sudoku.cells():
		for d in cell.dcs:
			if cell.dcs[d] != color:
				continue
			changed |= cell.exclude({d})
			if verbose:
				print('    > Cell %s can only be %s' % (cell.cell_name(),
					cell.value_string()))
	return changed

def medusa_check_full_cells(sudoku, print_start, verbose):
	changed = False
	for cell in sudoku.cells():
		if len(set(cell.dcs.values())) != 2:
			continue
		cell_changed = cell.include_only(cell.dcs.keys())
		if verbose and cell_changed:
			if not changed:
				print_start()
				print(' - Find cells with candidates in both colors and others uncolored')
			print('    * Cell %s can only be %s' % (cell.cell_name(),
				cell.value_string()))
		changed |= cell_changed
	return changed

def medusa_check_emptied_cells(sudoku, print_start, verbose):
	changed = False
	for cell in sudoku.cells():
		if cell.solved():
			continue
		seen = sudoku.seen_from(cell.x, cell.y)
		for d in cell.ds - set(cell.dcs):
			d_colors = {c.dcs[d] for c in seen if d in c.dcs}
			if len(d_colors) != 2:
				continue
			cell_changed = cell.exclude({d})
			if verbose and cell_changed:
				if not changed:
					print_start()
					print(' - Find cells with an uncolored candidate that can be seen in both colors')
				print('    * Cell %s can only be %s, since it can see %d in both colors' %
					(cell.cell_name(), cell.value_string(), d))
			changed |= cell_changed
	return changed

def medusa_check_partial_cells(sudoku, print_start, verbose):
	changed = False
	for cell in sudoku.cells():
		if len(cell.dcs) != 1:
			continue
		d_colored = cell.dcs.keys()[0]
		d_color = cell.dcs[d_colored]
		seen = sudoku.seen_from(cell.x, cell.y)
		for d in cell.ds - {d_colored}:
			if not any(c for c in seen if c.dcs.get(d, Color.NEITHER) == ~d_color):
				continue
			cell_changed = cell.exclude({d})
			if verbose and cell_changed:
				if not changed:
					print_start()
					print(' - Find cells with a candidate in one color that can see it in the other color')
				print('    * Cell %s can only be %s, since its %d is %s and it can see %d in %s' %
					(cell.cell_name(), cell.value_string(), d_colored,
						d_color, d, ~d_color))
			changed |= cell_changed
	return changed

@Sudoku.strategy('bi-value cell forcing chain', 17)
def solve_cell_forcing_chains(sudoku, verbose):
	"""Color two candidates of a bi-value cell red and blue, and propagate the
	colors outward as if they were the actual values of that cell; then exclude
	candidates based on the derived contradictions or tautologies."""
	return any(solve_cell_forcing_chain_from(sudoku, x, y, verbose)
		for y, x in product(range(9), range(9)))

def solve_cell_forcing_chain_from(sudoku, x, y, verbose):
	start_cell = sudoku.cell(x, y)
	if not start_cell.bi_value():
		return False
	p, q = sorted(start_cell.ds)
	start_cell.dcs[p], start_cell.dcs[q] = Color.RED, Color.BLUE
	while (forcing_chain_propagate_naked_color(sudoku, Color.RED, verbose) or
		forcing_chain_propagate_naked_color(sudoku, Color.BLUE, verbose) or
		forcing_chain_propagate_hidden_color(sudoku, Color.RED, verbose) or
		forcing_chain_propagate_hidden_color(sudoku, Color.BLUE, verbose)):
		pass
	print_start = lambda: (cell_forcing_chain_print_start(sudoku, start_cell), print(sudoku))
	changed = (forcing_chain_check_seen_contradictions(sudoku, print_start, verbose) or
		forcing_chain_check_unit_contradictions(sudoku, print_start, verbose))
	if not changed:
		changed |= forcing_chain_check_purple_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= forcing_chain_check_full_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= forcing_chain_check_emptied_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= forcing_chain_check_seen_cells(sudoku, print_start, verbose)
	for cell in sudoku.cells():
		cell.dcs = {}
	return changed

def cell_forcing_chain_print_start(sudoku, start_cell):
	p, q = sorted(start_cell.ds)
	print(' - Start from cell %s, coloring %d %s and %d %s' %
		(start_cell.cell_name(), p, start_cell.dcs[p], q, start_cell.dcs[q]))

@Sudoku.strategy('dual unit forcing chain', 18)
def solve_unit_forcing_chains(sudoku, verbose):
	"""Color two bi-location candidates in a unit red and blue, and propagate
	the colors outward as if they were the actual values of those cells; then
	exclude candidates based on the derived contradictions or tautologies."""
	return any(solve_unit_forcing_chain_from(sudoku, unit_type, i, d, verbose)
		for unit_type, i, d in product(Sudoku.UNIT_TYPES, range(9), Cell.VALUES))

def solve_unit_forcing_chain_from(sudoku, unit_type, i, d, verbose):
	unit = sudoku.unit(unit_type, i)
	start_cells = [c for c in unit if d in c.ds]
	if len(start_cells) != 2:
		return False
	start_red, start_blue = sorted(start_cells)
	start_red.dcs[d], start_blue.dcs[d] = Color.RED, Color.BLUE
	while (forcing_chain_propagate_naked_color(sudoku, Color.RED, verbose) or
		forcing_chain_propagate_naked_color(sudoku, Color.BLUE, verbose) or
		forcing_chain_propagate_hidden_color(sudoku, Color.RED, verbose) or
		forcing_chain_propagate_hidden_color(sudoku, Color.BLUE, verbose)):
		pass
	print_start = lambda: (unit_forcing_chain_print_start(sudoku, unit_type, i, d), print(sudoku))
	changed = (forcing_chain_check_seen_contradictions(sudoku, print_start, verbose) or
		forcing_chain_check_unit_contradictions(sudoku, print_start, verbose))
	if not changed:
		changed |= forcing_chain_check_purple_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= forcing_chain_check_full_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= forcing_chain_check_emptied_cells(sudoku, print_start, verbose)
		if changed: print_start = lambda: None
		changed |= forcing_chain_check_seen_cells(sudoku, print_start, verbose)
	for cell in sudoku.cells():
		cell.dcs = {}
	return changed

def unit_forcing_chain_print_start(sudoku, unit_type, i, d):
	unit = sudoku.unit(unit_type, i)
	start_cells = [c for c in unit if d in c.ds]
	start_red, start_blue = sorted(start_cells)
	print(' - Start from %s %s, coloring %d %s in cell %s and %s in cell %s' %
		(unit_type, sudoku.unit_name(unit_type, i), d, start_red.dcs[d],
			start_red.cell_name(), start_blue.dcs[d], start_blue.cell_name()))

def forcing_chain_propagate_naked_color(sudoku, color, verbose):
	colored = False
	for cell in sudoku.cells():
		if cell.solved() or any(r & color for r in cell.dcs.values()):
			continue
		seen = sudoku.seen_from(cell.x, cell.y)
		seen_colored = union({d for d in c.dcs if c.dcs[d] & color} for c in seen)
		candidates = cell.ds - seen_colored
		if len(candidates) == 1:
			d, = candidates
			cell.dcs[d] = cell.dcs.get(d, Color.NEITHER) | color
			colored = True
	return colored

def forcing_chain_propagate_hidden_color(sudoku, color, verbose):
	colored = False
	for cell in sudoku.cells():
		if cell.solved() or any(r & color for r in cell.dcs.values()):
			continue
		seen = sudoku.seen_from(cell.x, cell.y)
		for unit_type, d in product(Sudoku.UNIT_TYPES, cell.ds):
			seen_unit = sudoku.unit_without(unit_type, cell.x, cell.y)
			if all(c.dcs.get(d, Color.NEITHER) == ~color for c in seen_unit):
				cell.dcs[d] = cell.dcs.get(d, Color.NEITHER) | color
				colored = True
	return colored

def forcing_chain_check_seen_contradictions(sudoku, print_start, verbose):
	for cell in sudoku.cells():
		if cell.dcs:
			continue
		seen = sudoku.seen_from(cell.x, cell.y)
		seen_colors = {d: {c.dcs[d] for c in seen if d in c.dcs} for d in cell.ds}
		seen_color = None
		if all({Color.RED, Color.PURPLE} & seen_colors[d] for d in cell.ds):
			seen_color = Color.RED
		elif all({Color.BLUE, Color.PURPLE} & seen_colors[d] for d in cell.ds):
			seen_color = Color.BLUE
		else:
			continue
		if verbose:
			print_start()
			print(' - Find cells that can see all their candidates in the same color')
			print(' * Cell %s can see all its candidates %s in %s' %
				(cell.cell_name(), cell.value_string(), seen_color))
		return forcing_chain_use_color(sudoku, ~seen_color, verbose)
	return False

def forcing_chain_check_unit_contradictions(sudoku, print_start, verbose):
	for unit_type, i, d in product(Sudoku.UNIT_TYPES, range(9), Cell.VALUES):
		unit = sudoku.unit(unit_type, i)
		colors = [c.dcs[d] for c in unit if d in c.dcs]
		dup_color = Color.NEITHER
		if colors.count(Color.RED) > 1 or Color.RED in colors and Color.PURPLE in colors:
			dup_color = Color.RED
		elif colors.count(Color.BLUE) > 1 or Color.BLUE in colors and Color.PURPLE in colors:
			dup_color = Color.BLUE
		else:
			continue
		if verbose:
			print_start()
			print(' - Find a unit with multiple cells with the same candidate in the same color')
			dup_cell_names = [c.cell_name() for c in unit
				if c.dcs.get(d, Color.NEITHER) & dup_color]
			print(' - %s %s has multiple cells (%s) with candidate %d colored %s' %
				(unit_type.capitalize(), sudoku.unit_name(unit_type, i),
					', '.join(dup_cell_names), d, dup_color))
		return forcing_chain_use_color(sudoku, ~dup_color, verbose)
	return False

def forcing_chain_use_color(sudoku, color, verbose):
	if verbose:
		print(' - Use all candidates colored %s' % color)
	changed = False
	for cell in sudoku.cells():
		for d in cell.dcs:
			if not (cell.dcs[d] & color):
				continue
			changed |= cell.include_only({d})
			if verbose:
				print(' * Cell %s can only be %s' % (cell.cell_name(),
					cell.value_string()))
	return changed

def forcing_chain_check_purple_cells(sudoku, print_start, verbose):
	changed = False
	for cell in sudoku.cells():
		if Color.PURPLE not in cell.dcs.values():
			continue
		d, = [d for d in cell.dcs if cell.dcs[d] == Color.PURPLE]
		cell_changed = cell.include_only({d})
		if verbose and cell_changed:
			if not changed:
				print_start()
				print(' - Find cells with candidates colored purple')
			print('    > Cell %s can only be %s' % (cell.cell_name(),
				cell.value_string()))
		changed |= cell_changed
	return changed

def forcing_chain_check_full_cells(sudoku, print_start, verbose):
	changed = False
	for cell in sudoku.cells():
		if len(set(cell.dcs.values())) != 2:
			continue
		cell_changed = cell.include_only(cell.dcs.keys())
		if verbose and cell_changed:
			if not changed:
				print_start()
				print(' - Find cells with candidates in both colors and others uncolored')
			print('    > Cell %s can only be %s' % (cell.cell_name(),
				cell.value_string()))
		changed |= cell_changed
	return changed

def forcing_chain_check_emptied_cells(sudoku, print_start, verbose):
	changed = False
	for cell in sudoku.cells():
		if cell.solved():
			continue
		seen = sudoku.seen_from(cell.x, cell.y)
		for d in cell.ds - set(cell.dcs):
			d_colors = {c.dcs[d] for c in seen if d in c.dcs}
			if len(d_colors) != 2:
				continue
			cell_changed = cell.exclude({d})
			if verbose and cell_changed:
				if not changed:
					print_start()
					print(' - Find cells with an uncolored candidate that can be seen in both colors')
				print('    * Cell %s can only be %s, since it can see %d in both colors' %
					(cell.cell_name(), cell.value_string(), d))
			changed |= cell_changed
	return changed

def forcing_chain_check_seen_cells(sudoku, print_start, verbose):
	changed = False
	for cell in sudoku.cells():
		if len(cell.dcs) != 1:
			continue
		d_colored = cell.dcs.keys()[0]
		d_color = cell.dcs[d_colored]
		seen = sudoku.seen_from(cell.x, cell.y)
		for d in cell.ds - {d_colored}:
			if not any(c for c in seen if c.dcs.get(d, Color.NEITHER) & ~d_color):
				continue
			cell_changed = cell.exclude({d})
			if verbose and cell_changed:
				if not changed:
					print_start()
					print(' - Find cells with a candidate in one color that can see it in the other color')
				print('    * Cell %s can only be %s, since its %d is %s and it can see %d in %s' %
					(cell.cell_name(), cell.value_string(), d_colored,
						d_color, d, ~d_color))
			changed |= cell_changed
	return changed

@Sudoku.strategy('Nishio forcing chain', 19)
def solve_nishio_forcing_chains(sudoku, verbose):
	"""Turn a candidate in an unsolved cell on, and propagate other on/off
	candidates outward as if the starting one were actually on; then
	exclude candidates based on the derived contradictions or tautologies."""
	return any(solve_nishio_forcing_chain_from(sudoku, start_cell, verbose)
		for start_cell in sorted(sudoku.cells(), key=lambda c: (len(c.ds), c)))

def solve_nishio_forcing_chain_from(sudoku, start_cell, verbose):
	if start_cell.solved():
		return False
	for d in start_cell.ds:
		start_cell.dcs[d] = Color.BLUE
		while (nishio_forcing_chain_propagate_on(sudoku, verbose) or
			nishio_forcing_chain_propagate_off(sudoku, verbose)):
			pass
		print_start = lambda: (nishio_forcing_chain_print_start(sudoku, start_cell, d), print(sudoku))
		if (nishio_forcing_chain_check_cell_contradictions(sudoku, print_start, verbose) or
			nishio_forcing_chain_check_unit_contradictions(sudoku, print_start, verbose)):
			start_cell.exclude({d})
			if verbose:
				print(' * Cell %s can only be %s' % (start_cell.cell_name(),
					start_cell.value_string()))
			for cell in sudoku.cells():
				cell.dcs = {}
			return True
		for cell in sudoku.cells():
			cell.dcs = {}
	return False

def nishio_forcing_chain_print_start(sudoku, start_cell, d):
	print(' - Start chains from cell %s, turning %d on' %
		(start_cell.cell_name(), d))

@Sudoku.strategy('anti-Nishio forcing chain', 20)
def solve_anti_nishio_forcing_chains(sudoku, verbose):
	"""Turn a candidate in an unsolved cell off, and propagate other on/off
	candidates outward as if the starting one were actually off; then
	exclude candidates based on the derived contradictions or tautologies."""
	return any(solve_anti_nishio_forcing_chain_from(sudoku, start_cell, verbose)
		for start_cell in sorted(sudoku.cells(), key=lambda c: (len(c.ds), c)))

def solve_anti_nishio_forcing_chain_from(sudoku, start_cell, verbose):
	if start_cell.solved():
		return False
	for d in start_cell.ds:
		start_cell.dcs[d] = Color.RED
		while (nishio_forcing_chain_propagate_on(sudoku, verbose) or
			nishio_forcing_chain_propagate_off(sudoku, verbose)):
			pass
		print_start = lambda: (anti_nishio_forcing_chain_print_start(sudoku, start_cell, d), print(sudoku))
		if (nishio_forcing_chain_check_cell_contradictions(sudoku, print_start, verbose) or
			nishio_forcing_chain_check_unit_contradictions(sudoku, print_start, verbose)):
			start_cell.include_only({d})
			if verbose:
				print(' * Cell %s can only be %s' % (start_cell.cell_name(),
					start_cell.value_string()))
			for cell in sudoku.cells():
				cell.dcs = {}
			return True
		for cell in sudoku.cells():
			cell.dcs = {}
	return False

def anti_nishio_forcing_chain_print_start(sudoku, start_cell, d):
	print(' - Start chains from cell %s, turning %d off' %
		(start_cell.cell_name(), d))

def nishio_forcing_chain_propagate_on(sudoku, verbose):
	colored = False
	for cell in sudoku.cells():
		if cell.solved():
			continue
		seen = sudoku.seen_from(cell.x, cell.y)
		for d in cell.ds:
			if cell.dcs.get(d, Color.NEITHER) & Color.BLUE:
				continue
			if all(cell.dcs.get(p, Color.NEITHER) & Color.RED for p in cell.ds - {d}):
				cell.dcs[d] = cell.dcs.get(d, Color.NEITHER) | Color.BLUE
				colored = True
				break
			elif all(c.dcs.get(d, Color.NEITHER) & Color.RED for c in seen
				if not c.solved() and d in c.ds):
				cell.dcs[d] = cell.dcs.get(d, Color.NEITHER) | Color.BLUE
				colored = True
				break
	return colored

def nishio_forcing_chain_propagate_off(sudoku, verbose):
	colored = False
	for cell in sudoku.cells():
		if cell.solved():
			continue
		seen = sudoku.seen_from(cell.x, cell.y)
		for d in cell.ds:
			if (not any(cell.dcs.get(p, Color.NEITHER) & Color.RED for p in cell.ds - {d}) and
				(cell.dcs.get(d, Color.NEITHER) & Color.BLUE)):
				cell.dcs.update({p: cell.dcs.get(p, Color.NEITHER) | Color.RED
					for p in cell.ds - {d}})
				colored = True
				break
			elif (not (cell.dcs.get(d, Color.NEITHER) & Color.RED) and
				any(c.dcs.get(d, Color.NEITHER) & Color.BLUE for c in seen)):
				cell.dcs[d] = cell.dcs.get(d, Color.NEITHER) | Color.RED
				colored = True
	return colored

def nishio_forcing_chain_check_cell_contradictions(sudoku, print_start, verbose):
	for cell in sudoku.cells():
		if Color.PURPLE in cell.dcs.values():
			if verbose:
				print_start()
				print(' - Find a cell with a candidate turned both on and off')
				purple_candidates = {d for d in cell.dcs if cell.dcs[d] == Color.PURPLE}
				print(' - Cell %s has %s turned on and off' %
					(cell.cell_name(), set_string(purple_candidates)))
			return True
		if all(cell.dcs.get(d, Color.NEITHER) & Color.RED for d in cell.ds):
			if verbose:
				print_start()
				print(' - Find a cell with all candidates turned off')
				print(' - Cell %s has all candidates %s turned off' %
					(cell.cell_name(), cell.value_string()))
			return True
	return False

def nishio_forcing_chain_check_unit_contradictions(sudoku, print_start, verbose):
	for unit_type, i, d in product(Sudoku.UNIT_TYPES, range(9), Cell.VALUES):
		unit = sudoku.unit(unit_type, i)
		if all(c.dcs.get(d, Color.NEITHER) & Color.RED for c in unit):
			if verbose:
				print_start()
				print(' - Find a unit with all of a candidate turned off')
				red_cells = [c for c in unit if c.dcs.get(d, Color.NEITHER) & Color.RED]
				print(' * In %s %s, cells (%s) have %d turned off' %
					(unit_type, sudoku.unit_name(unit_type, i),
						', '.join(c.cell_name() for c in red_cells), d))
			return True
		blue_cells = [c for c in unit if (c.dcs.get(d, Color.NEITHER) & Color.BLUE) or
			c.value() == d]
		if len(blue_cells) > 1:
			if verbose:
				print_start()
				print(' - Find a unit with more than one of a candidate turned on')
				print(' * In %s %s, cells (%s) have %d turned on' %
					(unit_type, sudoku.unit_name(unit_type, i),
						', '.join(c.cell_name() for c in blue_cells), d))
			return True
	return False

@Sudoku.strategy('2-cell subset exclusion', 21)
def solve_2_cell_subset_exclusion(sudoku, verbose):
	"""Find a pair of cells that would lead to a contradiction if one of them
	actually were a certain candidate, and exclude that candidate."""
	return solve_n_cell_subset_exclusion(sudoku, 2, verbose)

@Sudoku.strategy('3-cell subset exclusion', 22)
def solve_3_cell_subset_exclusion(sudoku, verbose):
	"""Find a triple of cells that would lead to a contradiction if one of them
	actually were a certain candidate, and exclude that candidate."""
	return solve_n_cell_subset_exclusion(sudoku, 3, verbose)

def solve_n_cell_subset_exclusion(sudoku, n, verbose):
	unsolved_cells = [c for c in sudoku.cells() if not c.solved()]
	for subset in combinations(unsolved_cells, n):
		seen = intersection(sudoku.seen_from(c.x, c.y) for c in subset)
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
	return False

@Sudoku.strategy('guessing', 999)
def solve_guessing(sudoku, verbose):
	"""Guess a candidate for a cell and see if a contradiction occurs."""
	return any(solve_guessing_from(sudoku, start_cell, verbose)
		for start_cell in sorted(sudoku.cells(), key=lambda c: (len(c.ds), c)))

def solve_guessing_from(sudoku, start_cell, verbose):
	if start_cell.solved():
		return False
	for d in start_cell.ds:
		guess = sudoku.copy()
		guess.cell(start_cell.x, start_cell.y).include_only({d})
		try:
			guess.solve(exclude=[999], verbose=False)
			guess.verify()
		except:
			start_cell.exclude({d})
			if verbose:
				print(sudoku)
				print(' * Cell %s cannot be %d (guessed; there is a contradiction)' %
					(start_cell.cell_name(), d))
			return True
		if guess.solved():
			start_cell.include_only({d})
			if verbose:
				print(sudoku)
				print(' * Cell %s is %d (guessed successfully)' %
					(start_cell.cell_name(), d))
			return True
	return False
