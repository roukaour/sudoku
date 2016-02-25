#!/usr/bin/python

from __future__ import print_function

from board import Sudoku
from strategies import *

from argparse import ArgumentParser
import sys

def solve_board(board, guess, verbose):
	"""Solve a single board."""
	board = Sudoku(board)
	exclude = None if guess else [999]
	board.solve(exclude=exclude, verbose=verbose)
	board.verify()

def solve_boards(file, guess, verbose):
	"""Solve each board in a text file."""
	if verbose:
		print('#', 'solved?', 'board', 'strategy', sep='\t')
	exclude = None if guess else [999]
	with open(file, 'r') as boards:
		for line in boards:
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			board = Sudoku(line)
			n = board.num_solved()
			hardest = board.solve(exclude=exclude)
			try:
				board.verify()
			except:
				print('*** ERROR:', line)
				Sudoku(line).solve(exclude=exclude, verbose=True)
				break
			if verbose:
				print(board.num_solved() - n, 'TRUE' if board.solved() else 'FALSE',
					line, hardest, sep='\t')

def main():
	parser = ArgumentParser(description='Human-style Sudoku solver')
	parser.add_argument('-g', '--guess', action='store_true',
		help='allow guessing to solve')
	parser.add_argument('-q', '--quiet', action='store_true',
		help='solve a board without printing anything')
	parser.add_argument('-f', '--file',
		help='solve each board in a text file and output overall results as tab-separated data')
	parser.add_argument('BOARD', nargs='?',
		help='a single board to solve')
	args = vars(parser.parse_args())
	if args['BOARD']:
		solve_board(args['BOARD'], args['guess'], not args['quiet'])
	elif args['file']:
		solve_boards(args['file'], args['guess'], not args['quiet'])
	else:
		parser.print_usage()

if __name__ == '__main__':
	main()
