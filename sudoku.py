#!/usr/bin/python

from __future__ import print_function

from board import Sudoku
from strategies import *

from argparse import ArgumentParser

def solve_board(board, quiet):
	"""Solve a single board."""
	board = Sudoku(board)
	board.solve(not quiet)
	board.verify()

def solve_boards(file):
	"""Solve each board in a text file."""
	print('#', 'solved?', 'board', 'method', sep='\t')
	with open(file, 'r') as boards:
		for line in boards:
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			board = Sudoku(line)
			n = board.num_solved()
			hardest = board.solve()
			try:
				board.verify()
			except:
				print('*** ERROR:', line)
				Sudoku(line).solve(True)
				break
			print(board.num_solved() - n, 'TRUE' if board.solved() else 'FALSE',
				line, hardest, sep='\t')

def main():
	parser = ArgumentParser(description='Human-style Sudoku solver')
	parser.add_argument('-q', '--quiet', action='store_true',
		help='solve a board without printing anything')
	parser.add_argument('-f', '--file',
		help='solve each board in a text file and output overall results as tab-separated data')
	parser.add_argument('BOARD', nargs='?',
		help='a single board to solve')
	args = vars(parser.parse_args())
	if args['BOARD']:
		solve_board(args['BOARD'], args['quiet'])
	elif args['file']:
		solve_boards(args['file'])
	else:
		parser.print_usage()

if __name__ == '__main__':
	main()
