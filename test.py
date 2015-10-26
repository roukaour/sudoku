#!/usr/bin/python

# http://www.stolaf.edu/people/hansonr/sudoku/top95-analysis.htm
# http://www.sudokuwiki.org/sudoku.htm
# http://www.sudokuwiki.org/Strategy_Families
# http://www.sudokuwiki.org/Weekly_Sudoku.asp
# http://www.sadmansoftware.com/sudoku/solvingtechniques.php
# http://www.thonky.com/sudoku/

from __future__ import print_function

from sudoku import *

def test_solve_methods(solver, verbose=False):
	if solver.solved():
		return (False, (0, 'nothing'))
	if solver.solve_strip_naked_singletons(verbose):
		return (True, (1, 'naked singletons'))
	if solver.solve_hidden_n_tuples(1, verbose):
		return (True, (1.5, 'hidden singletons'))
	for n in range(2, 5):
		if solver.solve_naked_n_tuples(n, verbose):
			return (True, (n, 'naked %ss' % n_tuple_name(n)))
		if solver.solve_hidden_n_tuples(n, verbose):
			return (True, (n+0.5, 'hidden %ss' % n_tuple_name(n)))
	for unit_type in Sudoku.UNIT_TYPES:
		if solver.solve_unit_intersection_removals(unit_type, verbose):
			intersection_plurals = {
				'row': "block+row reductions",
				'column': "block+column reductions",
				'block': 'pointing pairs/triples'}
			intersection_plural = intersection_plurals[unit_type]
			return (True, (5, intersection_plural))
	for n in range(2, 5):
		if solver.solve_n_fish(n, verbose):
			n_fish_name = {2: 'X-wing', 3: 'swordfish', 4: 'jellyfish'}[n]
			return (True, (n+4, n_fish_name))
	if solver.solve_3d_medusas(verbose):
		return (True, (9, '3D Medusas'))
	for n in range(2, 4):
		if solver.solve_n_cell_subset_exclusion(n, verbose):
			return (True, (n+8, '%d-cell subset exclusion' % n))
	return (False, (-1, 'unsolved'))
	
def test_solve(solver, verbose=False):
	if solver.solved():
		if verbose:
			print('Already solved!')
		return (True, 'nothing')
	if verbose:
		print('Solving %r' % solver)
	num_solved = solver.num_solved()
	hardest = (-1, 'unsolved')
	while True:
		worked, method = test_solve_methods(solver, verbose)
		if not worked:
			break
		if method[0] > hardest[0]:
			hardest = method
	if verbose:
		if solver.solved():
			print('Completely solved!')
		else:
			print('...Cannot solve further (solved %d cells)' %
				(solver.num_solved() - num_solved))
	return (solver.solved(), hardest[1])

def test_cases():
	s = Sudoku('000000010400000000020000000000050407008000300001090000300400200050100000000806000') # hidden singleton
	s = Sudoku('000000016000900080500000000405000300000100500000800000600040200000030070010000000') # naked pair
	s = Sudoku('000000012008030000000000040120500000000004700060000000507000300000620000000100000') # hidden pair
	s = Sudoku('000000054700030000000000000000400016380070000020000000000500800105000000006000300') # naked triple
	s = Sudoku('000000031080000070000920000401000000000200800300000000090000250000080600000001000') # hidden triple
	s = Sudoku('000100030720000000000000008300000007000640000000000200061000050000070600000008400') # hidden quad
	s = Sudoku('000000013400200000600000000000460500010000007200500000000031000000000420080000000') # row's pointing pair/triple
	s = Sudoku('000000021300050000000000000500630000010000080000000900704000600600200000000108000') # column's pointing pair/triple
	s = Sudoku('000002040030000600050070000800000020000600010000350000200000900000900300100000000') # block+line reduction
	s = Sudoku('000070900020600000500000300040000021700030000000000000000201080900000700000400000') # X-wing
	s = Sudoku('050400000000030800000000001300080700060000050000200000000506040108000300000000000') # swordfish
	s = Sudoku('000000013040000080200060000609000400000800000000300000030100500000040706000000000') # 3D Medusa
	s = Sudoku('300050001000010000000000060002600300000204000000000005850000700000900020100000000') # 2-cell subset exclusion
	s = Sudoku('010000020000800600000003000000004300002010000800000090400070503000200000000000400') # 3-cell subset exclusion
	s = Sudoku('000000012400090000000000050070200000600000400000108000018000000000030700502000000') # solves 4
	s = Sudoku('000000608900002000000000300500060070000800000000030000020007500038100000000000040') # solves 0
	s = Sudoku('000060000020904060400070009030000092009080500100000030500000001090206040000050000') # unsolvable (solves 10)
	s = Sudoku('100007090030020008009600500005300900010080002600004000300000010041000007007000300') # "Escargot" (unsolvable)
	s.solve(verbose=True)
	s.verify()
	print(s)

def test_boards():
	print('#', 'solved?', 'board', 'method', sep='\t')
	with open('boards.txt', 'r') as boards:
		for line in boards:
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			s = Sudoku(line)
			n = s.num_solved()
			solved, hardest = test_solve(s)
			try:
				s.verify()
			except:
				print('*** ERROR:', line)
				Sudoku(line).solve(True)
				break
			print(s.num_solved() - n, 'TRUE' if s.solved() else 'FALSE', line, hardest, sep='\t')

if __name__ == '__main__':
	#test_boards()
	s = Sudoku('103450000000000020400807000381070000600300000000000900000500004000002800005061000')
	s.solve(verbose=True)
	s.verify()
	print(s)
