# Sudoku

A Sudoku solver that uses human strategies.

* [Naked singletons, pairs, triples, and quads](http://www.sudokuwiki.org/Naked_Candidates)
* [Hidden singletons, pairs, triples, and quads](http://www.sudokuwiki.org/Hidden_Candidates)
* [Pointing pairs and triples](http://www.sudokuwiki.org/Intersection_Removal)
* [Block+line reductions](http://www.sudokuwiki.org/Intersection_Removal)
* [X-wing](http://www.sudokuwiki.org/X_Wing_Strategy),
  [Swordfish](http://www.sudokuwiki.org/Sword_Fish_Strategy), and
  [Jellyfish](http://www.sudokuwiki.org/Jelly_Fish_Strategy)
* [3D Medusas](http://www.sudokuwiki.org/3D_Medusa)
* [Subset exclusion](http://www.sudokuwiki.org/Aligned_Pair_Exclusion) (incomplete)

These strategies are insufficient to solve all boards. My intention is to
automate the strategies that I fully understand, since at that point doing them
myself is just busy work.

Other boards can apparently be solved with simpler strategies by
[Sudoku Wiki](http://www.sudokuwiki.org/sudoku.htm), but my solver resorts to
more complicated ones:

* 100000700006920000009308500000090008000072000350000007000001090600009410000640800
* 103450000000000020400807000381070000600300000000000900000500004000002800005061000
