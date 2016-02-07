# Sudoku

A Sudoku solver that uses human strategies.

* [Naked singles, pairs, triples, and quads](http://www.sudokuwiki.org/Naked_Candidates)
* [Hidden singles, pairs, triples, and quads](http://www.sudokuwiki.org/Hidden_Candidates)
* [Unit intersections](http://www.sudokuwiki.org/Intersection_Removal) (a.k.a.
  pointing pairs and box+line reductions)
* [X-wing](http://www.sudokuwiki.org/X_Wing_Strategy),
  [swordfish](http://www.sudokuwiki.org/Sword_Fish_Strategy), and
  [jellyfish](http://www.sudokuwiki.org/Jelly_Fish_Strategy)
* [3D Medusas](http://www.sudokuwiki.org/3D_Medusa) (a generalization of
  [simple coloring](http://www.sudokuwiki.org/Singles_Chains))
* Dual Medusas (3D Medusas that start with a bi-location value in a unit instead
  of a bi-value cell)
* [Bi-value cell forcing chains](http://www.sudokuwiki.org/Cell_Forcing_Chains)
  (including [grouped nodes](http://www.sudokuwiki.org/Grouped_X_Cycles))
* [Dual unit forcing chains](http://www.sudokuwiki.org/Unit_Forcing_Chains)
  (including [grouped nodes](http://www.sudokuwiki.org/Grouped_X_Cycles))
* [Subset exclusion](http://www.sudokuwiki.org/Aligned_Pair_Exclusion) (incomplete)

These strategies are insufficient to solve all boards. My intention is to
automate the strategies that I fully understand, since at that point doing them
myself is just busy work.

So far it can solve 99.1% of
[these 49,152 17-hint Sudoku](http://staffhome.ecm.uwa.edu.au/~00013890/sudokumin.php)
(only 438 are unsolvable). With the
[puzzles chosen by Peter Norvig](http://norvig.com/sudoku.html),
it can solve all 50 of the easy ones, 58 of the 95 hard ones, and 8 of the 11
hardest ones. However, all of the
[AI Sudoku Top 10](http://www.aisudoku.com/en/AIwME.html)
are unsolvable.
