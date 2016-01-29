#!/usr/bin/python

# http://www.sudokuwiki.org/sudoku.htm
# http://www.sudokuwiki.org/Strategy_Families
# http://www.sudokuwiki.org/Weekly_Sudoku.asp
# http://www.sadmansoftware.com/sudoku/solvingtechniques.php
# http://www.thonky.com/sudoku/

from __future__ import print_function

from sudoku import *

def test_boards():
	print('#', 'solved?', 'board', 'method', sep='\t')
	with open('boards.txt', 'r') as boards:
		for line in boards:
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			try:
				s = Sudoku(line)
				n = s.num_solved()
				hardest = s.solve()
			except:
				print('*** ERROR:', line)
				break
			try:
				s.verify()
			except:
				print('*** ERROR:', line)
				Sudoku(line).solve(True)
				break
			print(s.num_solved() - n, 'TRUE' if s.solved() else 'FALSE', line, hardest, sep='\t')

if __name__ == '__main__':
	test_boards()
