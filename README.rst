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

  >>> from pyscanprev import enable_scan_implicit, last, prepend
  >>> @enable_scan_implicit("prev")
  ... def gen():
  ...     yield [prev + el for el in range(15)]
  ...     yield {prev * x ** 2 for x in [1, -2, 3, 2]}
  ...     yield last(prev * x ** 2 for x in [1, -2, 3, 2])
  ...     yield [el - abs(prev) for el in prepend(15, [5, 6, 7, 8])]
  ...
  >>> g = gen()
  >>>         # List comprehension (scan)
  >>> next(g) # [prev + el for el in range(15)]
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]
  >>>         # Set comprehension
  >>> next(g) # {prev * x ** 2 for x in [1, -2, 3, 2]}
  {1, 4, 36, 144}
  >>>         # Generator expression (scan) + "last" (reduce/fold)
  >>> next(g) # last(prev * x ** 2 for x in [1, -2, 3, 2])
  144
  >>>         # Prepend a value (scan with explicit start)
  >>> next(g) # [el - abs(prev) for el in prepend(15, [5, 6, 7, 8])]
  [15, -10, -4, 3, 5]

Actually, Python already have a way to do that, but... `see by yourself`_\ .

The goal here is to find an easy way to read the previous value in a
generator expression and anything alike, so that the scan/fold
(accumulate/reduce) code can be written using them. Readability counts!

.. _`see by yourself`: examples/comparison.rst


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


The world without this package (rationale)
------------------------------------------

It's not usual nor widely known that the cross/cartesian product applied on
multiple "for" sections in a generator expression or a list/set/dict
comprehension allows more than one section to have the same target variable
name. But that provides the means to do something akin to a scan, for example
this cumulative sum (Tested in Python 2.6+ and 3.2+):

.. code-block:: python

  >>> [prev for prev in [0] for el in range(5) for prev in [prev + el]]
  [0, 1, 3, 6, 10]

Whose parts are:

.. code-block:: python

  [prev for prev in [start]
        for target in iterable
        for prev in [func(prev, target)]]

But that's a kludge, it's hard to grasp, hard to change/update/maintain,
fixed/locked in that "for" section order, and its behavior has some minor
details whose control would need to be external (e.g. using the first value
from the ``iterable`` as the ``start``). The ``prev`` variable appears at
least 4x in such structure and twice as a target. The first ``prev`` value is
``start``, which is just seen/used by the last "for" section in its first
``func`` call, whose result is assigned to ``prev`` before the whole list
comprehension appends/"yields" any output/result, since it's also the target
variable name in that "for" section. So ``start`` is never an output,
although everything starts with ``prev for prev in [start]``.

It's not only about aesthetics ou readability, but also about memorization.
Knowledge about the scan abstraction and about the Python language is probably
not enough for one to remember that structure.

As ``func`` in the previous example was essentially ``operator.add``, let's do
the same cumulative sum with ``itertools.accumulate`` (Python 3.2+):

.. code-block:: python

  >>> from itertools import accumulate
  >>> list(accumulate(range(5)))
  [0, 1, 3, 6, 10]

It seems the same, but here the first zero output is the ``next(range(5))``,
not the result of a sum or any other ``func`` for that matter (i.e., it
doesn't depend on ``func`` at all). To be really equivalent to the
3-for-sections list comprehension above, it would need to be something like:

.. code-block:: python

  >>> from itertools import accumulate
  >>> list(accumulate([0, 0, 1, 2, 3, 4]))[1:]
  [0, 1, 3, 6, 10]

There's a need to prepend ``0`` to ``range(5)``. What's going on here is that
``accumulate`` returns a generator that yields the values::

  [i0, i0+i1, i0+i1+i2, i0+i1+i2+i3, i0+i1+i2+i3+i4, ...]

Where "i\ :sub:`n`" is the n-th value from the ``iterable``. Every step
obviously uses the result from the previous step instead of summing all again,
and that's what the scan is all about. On the other hand, the 3-for-sections
list comprehension does this when ``func`` is the sum/add::

  [s+i0, s+i0+i1, s+i0+i1+i2, s+i0+i1+i2+i3, s+i0+i1+i2+i3+i4, ...]

Where "s" is the ``start``. Since Python 3.3, itertools.accumulate has an
optional second parameter, which should be a binary
operator/function/callable. For a given ``func``, the resulting generator
would yield, in order:

.. code-block:: python

  next(iterable),                  # result[0]
  func(result[0], next(iterable)), # result[1]
  func(result[1], next(iterable)), # result[2]
  func(result[2], next(iterable)), # result[3]
  ...

Where ``start`` is implicit as the first value from ``iterable``, and
``result`` is that output iterable itself seen as a sequence. To grasp the
difference, let's see a cumulative sum of squares starting with 3 in the
accumulator/register.

.. code-block:: python

  >>> list(accumulate([3, 5, 1, 1, 2], lambda x, y: x + y ** 2))
  [3, 28, 29, 30, 34]

To get the same result with a list comprehension, one would do:

.. code-block:: python

  >>> [3] + [x for x in [3]
  ...          for y in [5, 1, 1, 2]
  ...          for x in [x + y ** 2]]
  [3, 28, 29, 30, 34]

There's also a really old package in PyPI called functional_\ ,
whose last update was in 2006. Besides the without the distinction between
non-strict and "prime"/strict counterparts, it mimics all the
`4 scan and 4 fold Haskell functions`_\ , including their names
and their parameter order. From an external perpective,
``functional.scanl1`` and ``itertools.accumulate`` can be seen as almost the
same, the difference is that ``scanl1`` needs the function to be the first
argument and it isn't optional. On the other hand, ``functional.scanl`` needs
an extra "start" parameter. Both functions returns a generator:

.. code-block:: python

  >>> import functional, operator

  >>> # scanl (+) 0 [0..4]
  >>> list(functional.scanl(operator.add, 0, range(5)))
  [0, 0, 1, 3, 6, 10]

  >>> # scanl1 (+) [0..4]
  >>> list(functional.scanl1(operator.add, range(5)))
  [0, 1, 3, 6, 10]

  >>> # scanl1 (\x y -> x + y^2) [3, 5, 1, 1, 2]
  >>> list(functional.scanl1(lambda x, y: x + y ** 2, [3, 5, 1, 1, 2]))
  [3, 28, 29, 30, 34]

Both ``scanl`` and ``scanl1`` have a behavior different from that
3-for-sections list comprehension.

Python ``functools.reduce``, ``functional.foldl`` and ``functional.foldl1``
have all the same idea, which is to return the last value of the scan
resulting from the same given inputs to ``functional.scanl`` and
``functional.scanl1``. The ``reduce`` function can have an optional ``start``
as the 3rd and last argument, which gives to it both the behavior of both
``foldl``, that requires the ``start`` as the 2nd parameter, and ``foldl1``,
which uses the first iterable value as the start value. If there's a way to
modify generator expressions so that ``scanl/scanl1/accumulate`` can be
implemented with them with a good readability, the same would apply to reduce.

But, even for developers who like to think on these concepts as ready to use
abstractions stored in first class objects, here we got a parameter hell!
Their order is a mess:

* (iterable, func) -> ``itertools.accumulate``
* (func, start, iterable) -> ``functional.scanl``
* (func, iterable) -> ``functional.scanl1``, ``map``, ``filter``
* (func, iterable, [start]) -> ``functools.reduce``

The higher-order functions scan and fold appears respectively in
``itertools.accumulate`` and ``functools.reduce`` first-class objects
(functions are first-class objects in Python), which are quite easy for people
coming from a functional programming background to grasp, and far easier to
read/remember than the 3-for-sections list comprehension. One just neet to
know these two have their 2 parameters reversed, and that accumulate doesn't
have an optional external start value. It would be great to have an optional
start parameter on ``itertools.accumulate``, as well as a function signature
standardization, but the main purpose of this is just to get a cleaner
alternative to that 3-for-sections list comprehension.

.. _`functional`:
  https://pypi.python.org/pypi/bytecode

.. _`4 scan and 4 fold Haskell functions`:
  https://hackage.haskell.org/package/base/docs/Data-List.html

----

Copyright (C) 2016 Danilo de Jesus da Silva Bellini
