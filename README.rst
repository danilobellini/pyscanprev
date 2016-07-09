PyScanPrev
==========

Scan and reduce/fold as generator expressions and list/set comprehensions
with the previous output.

`Scan`_ is a high order function that can be seen as something between a
map and a reduce/fold, returning all steps of a fold. Since Python 3.3,
it's available in the function `itertools.accumulate`_\ .

This module has a ``enable_scan_implicit(name)`` decorator that allows
functions to have generator expressions and list/set comprehensions with
the variable name in its body for accessing the previous resulting value,
and a ``last`` function that makes it straightforward to write a reduce/fold
from the scan result.

.. _`scan`:
    https://en.wikipedia.org/wiki/Prefix_sum#Scan_higher_order_function

.. _`itertools.accumulate`:
    https://docs.python.org/3.3/library/itertools.html#itertools.accumulate


Example
-------

.. code-block:: python

  >>> from pyscanprev import enable_scan_implicit, last
  >>> @enable_scan_implicit("prev")
  ... def gen():
  ...     yield [prev + el for el in range(15)]
  ...     yield {prev * x ** 2 for x in [1, -2, 3, 2]}
  ...     yield last(prev * x ** 2 for x in [1, -2, 3, 2])
  ...
  >>> g = gen()
  >>> next(g) # List comprehension (scan)
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]
  >>> next(g) # Set comprehension
  {144, 1, 4, 36}
  >>> next(g) # Generator expression (scan) + "last" (reduce/fold)
  144

Compare that with the old fashioned way to do the same:

.. code-block:: python

  >>> import itertools, functools
  >>> list(itertools.accumulate(range(15)))
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]
  >>> set(itertools.accumulate([1, -2, 3, 2], lambda prev, x: prev * x ** 2))
  {144, 1, 4, 36}
  >>> functools.reduce(lambda prev, x: prev * x ** 2, [1, -2, 3, 2])
  144


Goal
----

Find an easy way to read the previous value in a generator expression and
anything alike, so that the scan/fold (accumulate/reduce) code can be written
using generator expressions and list comprehensions.

Actually, Python already have a way to do that, but... see by yourself.

.. code-block:: python

  >>> start, *iter = range(15)
  >>> [start] + [prev for prev in [start] for el in iter for prev in [prev + el]]
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]
  >>> start, *iter = [1, -2, 3, 2]
  >>> set.union({start}, {prev for prev in [start] for x in iter for prev in [prev * x ** 2]})
  {144, 1, 4, 36}
  >>> [prev for prev in [start] for x in iter for prev in [prev * x ** 2]][-1]
  144

The last one doesn't have a generator, but does almost the same. These are
possible because Python allows using the same variable twice in the multiple
for loop parts "cartesian product". But would you really do that?

Readability counts!


Tell me, how is that possible at all?
-------------------------------------

Magic! Some people say that's bytecode manipulation, but isn't that all the
same?


Installing
----------

You can either use pip::

  pip install --upgrade git+https://github.com/danilobellini/pyscanprev

Or setup.py directly::

  python3 setup.py install

This software depends on `bytecode`_\ , which requires Python 3.4+.

.. _`bytecode`:
  https://pypi.python.org/pypi/bytecode


----

Copyright (C) 2016 Danilo de Jesus da Silva Bellini
