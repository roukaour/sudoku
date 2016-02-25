# Sudoku

A Sudoku solver that uses human strategies.

* [Naked singles, pairs, triples, and quads](http://www.sudokuwiki.org/Naked_Candidates)
* [Hidden singles, pairs, triples, and quads](http://www.sudokuwiki.org/Hidden_Candidates)
* [Unit intersections](http://www.sudokuwiki.org/Intersection_Removal) (a.k.a.
  pointing pairs and box+line reductions)
* [X-wings](http://www.sudokuwiki.org/X_Wing_Strategy),
  [swordfish](http://www.sudokuwiki.org/Sword_Fish_Strategy), and
  [jellyfish](http://www.sudokuwiki.org/Jelly_Fish_Strategy)
* [Y-wings](http://www.sudokuwiki.org/Y_Wing_Strategy) (a.k.a. XY-wings) and
  [XYZ-wings](http://www.sudokuwiki.org/XYZ_Wing)
* [3D Medusas](http://www.sudokuwiki.org/3D_Medusa) (a generalization of
  [simple coloring](http://www.sudokuwiki.org/Singles_Chains))
* Dual Medusas (3D Medusas that start with a bi-location candidate in a unit
  instead of a bi-value cell)
* [Bi-value cell forcing chains](http://www.sudokuwiki.org/Cell_Forcing_Chains)
* [Dual unit forcing chains](http://www.sudokuwiki.org/Unit_Forcing_Chains)
* [Nishio forcing chains](http://www.sudokuwiki.org/Nishio_Forcing_Chains)
* Anti-Nishio forcing chains (Nishio forcing chains that start with a candidate
  digit off instead of on)
* [Subset exclusion](http://www.sudokuwiki.org/Aligned_Pair_Exclusion) (incomplete)
* Guessing individual cells (with the `-g` flag enabled)

These strategies are insufficient to solve all boards without guessing. My
intention is to automate the strategies that I fully understand, since at that
point doing them myself is just busy work.

So far it can solve 99.5% of
[these 49,151 17-hint Sudoku](http://staffhome.ecm.uwa.edu.au/~00013890/sudokumin.php)
(only 266 are unsolvable). With the
[puzzles chosen by Peter Norvig](http://norvig.com/sudoku.html),
it can solve all 50 of the easy ones, 64 of the 95 hard ones, and 9 of the 11
hardest ones. However, all of the
[AI Sudoku Top 10](http://www.aisudoku.com/en/AIwME.html)
are unsolvable. (With guessing, all boards are solvable.)

## Usage

* `./sudoku.py BOARD`  
  Solves the given board and shows steps.  
  e.g. `./sudoku.py 000000001000000020000003000000040500006000300007810000010020004030000070950000000`
* `./sudoku.py -f FILE`  
  Solves each board in the given file and outputs a TSV summary.  
  e.g. `stdbuf -oL ./sudoku.py -f boards.txt > solutions.tsv`
* `./sudoku.py -q BOARD`  
  Solves the given board without printing anything. Useful for measuring performance.  
  e.g. `time ./sudoku.py -q 000000001000000020000003000000040500006000300007810000010020004030000070950000000`
* `./sudoku.py -g BOARD` or `./sudoku.py -g -f FILE`  
  Solves the given board or file with guessing enabled.  
  e.g. `./sudoku.py -g 000000001000000020003004000000003500010060000720000080000108000000720000900000600`
