from __future__ import print_function

def flatten(L):
	"""Flatten an iterable of iterables into a single list."""
	return [i for x in L for i in x]

def chunk(L, n):
	"""Split an iterable into n-item chunks."""
	return zip(*[iter(L)] * n)

def transpose(L):
	"""Transpose an iterable of iterables."""
	return zip(*L)

def set_string(s):
	"""Return a string representation of a set that is sorted and uses braces."""
	return '{' + ', '.join(map(str, sorted(s))) + '}'

def n_tuple_name(n):
	"""Return the proper name of an n-tuple for given n."""
	names = {1: 'single', 2: 'pair', 3: 'triple', 4: 'quad'}
	return names.get(n, '%d-tuple' % n)

def any_equal(s):
	"""Return whether any elements in a list are equal."""
	return len(set(s)) < len(s)

def all_equal(s):
	"""Return whether all elements in a list are equal."""
	return all(all(x == y for y in s) for x in s)

def union(s):
	"""Return the mutual union of a collection of collections."""
	return reduce(set.union, s, set())

def intersection(s):
	"""Return the mutual intersection of a collection of collections."""
	return reduce(set.intersection, s)
