PyScanPrev
==========

.. image::
  https://img.shields.io/travis/danilobellini/pyscanprev/master.svg
  :target: https://travis-ci.org/danilobellini/pyscanprev
  :alt: Travis CI builds

.. image::
  https://img.shields.io/coveralls/danilobellini/pyscanprev/master.svg
  :target: https://coveralls.io/r/danilobellini/pyscanprev
  :alt: Coveralls coverage report

.. summary

Scan and reduce/fold as generator expressions and list/set
comprehensions that can access the previous iteration output.

.. summary end

Would you like to replace this:

.. code-block:: python

  reduce(lambda prev, x: abs(prev - x), [2, 3, 4, 5])

by this?

.. code-block:: python

  last(abs(prev - x) for x in [2, 3, 4, 5])

Why not?

.. code-block:: python

  >>> from functools import reduce
  >>> from pyscanprev import enable_scan, last
  >>> @enable_scan("prev")
  ... def evaluate(data):
  ...     return reduce(lambda prev, x: abs(prev - x), data), \
  ...            last(abs(prev - x) for x in data)
  >>> evaluate([2, 3, 4, 5])
  (2, 2)


Examples
--------

.. list-table::
  :header-rows: 1

  * - Example
    - Description

  * - `Comparison`_
    - Simple scan/accumulate and fold/reduce examples using the
      PyScanPrev resources, the Python standard library and
      the 3-for-section comprehensions for comparing readability
      and expressiveness.

  * - `Conditional Toggling`_
    - Sometimes feedback isn't really required, but you should at
      least store some state about what's going on in the input.
      That's the case in this example, which toggles/updates the
      state only for certain inputs, aLtErNaTiNg CaSeS, iGnOrInG oThEr
      ChArAcTeRs. Historically, PyScanPrev was created after thinking
      on how would be the simplest way to solve the problem described
      in this example.

  * - `Examples from the itertools.accumulate documentation`_
    - This is a copy and an adaptation of the ``itertools.accumulate``
      examples in the Python documentation to use the PyScanPrev
      comprehensions instead of that standard library function. The
      examples include:

      - running product
      - running maximum
      - amortization tables
      - chaotic logistic map

  * - `Factorial and Multiplication`_
    - Fold/reduce factorial and multiplication / product of a sequence
      implementation using PyScanPrev.

  * - `Fibonacci`_
    - Fibonacci sequence with PyScanPrev.

  * - `Gray Code`_
    - Generating Gray codes using the definition is slower than using
      bitwise operations, but the recursive definition can be written
      as a scan/fold expression and is useful for testing, as this
      example shows.

  * - `Single pole lowpass IIR Filter`_
    - DSP (Digital Signal Processing) applications ofter requires
      feedback, i.e., accessing some previous output value in a
      process. PyScanPrev can be used to write simple signal
      processing models like IIR (Infinite Impuse Response) linear
      filters. This is an example with a single pole lowpass digital
      filter. For testing and displaying the results, this example
      uses `AudioLazy`_ and `hipsterplot`_\ .

  * - `State-space model`_
    - Simulation of linear discrete time modeling in control
      engineering. The example gives an implementation of both time
      varying and time invariant state-space models. These models are
      then used to simulate:

      - an accumulator
      - a LTI (Linear Time Invariant) continuous time
        mass-spring-damper SHM (Simple Harmonic Motion) model
      - a linear time varying "leaking bucket"-spring-damper model
      - another LTI IIR filter, designed from the difference equation
        and simulated as a state-space model, compared with the
        `AudioLazy`_ results

      The discretization process is included in the example, and the
      simulations use `hipsterplot`_\  to plot the motion
      path/trajectory. This example includes an explanation/proof to
      the conversion from difference equations to a state-space model
      (via Z Transform).

.. _`Comparison`:
  examples/comparison.rst
.. _`Conditional Toggling`:
  examples/conditional-toggling.rst
.. _`Examples from the itertools.accumulate documentation`:
  examples/itertools-accumulate-docs.rst
.. _`Factorial and Multiplication`:
  examples/factorial-prod.rst
.. _`Fibonacci`:
  examples/fibonacci.rst
.. _`Gray Code`:
  examples/gray.rst
.. _`Single pole lowpass IIR Filter`:
  examples/iir-filter.rst
.. _`State-space model`:
  examples/state-space.rst

.. _`AudioLazy`: https://github.com/danilobellini/audiolazy
.. _`hipsterplot`: https://github.com/imh/hipsterplot


Why "Scan"?
-----------

`Scan`_ is a high order function that can be seen as something between
the map and the reduce (fold) functions, returning all steps of a
fold. Since Python 3.3, it's available in the function
`itertools.accumulate`_\ .

The goal here is to find an easy way to read the previous value in a
generator expression and anything alike, so that the scan/fold
(accumulate/reduce) code can be written using them.
`Readability counts`_\ !

.. _`Scan`:
  https://en.wikipedia.org/wiki/Prefix_sum#Scan_higher_order_function
.. _`itertools.accumulate`:
  https://docs.python.org/library/itertools.html#itertools.accumulate
.. _`Readability counts`:
  https://www.python.org/dev/peps/pep-0020


Package contents
----------------

.. list-table::

  * -
      .. code-block:: python

        enable_scan(name)

      Decorator that allows functions to have generator expressions
      and list/set comprehensions with a variable (the one with the
      given name) in its body for accessing the previous resulting
      value.

  * -
      .. code-block:: python

        last(iterable)

      Gets the last value from an iterable, making it straightforward
      to write a reduce/fold from the scan result.

  * -
      .. code-block:: python

        prepend(value, iterable)

      A version of ``[value] + some_list`` for general iterables,
      returning a generator. This function was created to allow
      PyScanPrev-enabled generator expressions and list/set
      comprehensions to include an explicit start value, but it can be
      used to prepend a value in any context, e.g. to force a start
      value on ``itertools.accumulate``.

  * -
      .. code-block:: python

        scan(func, iterable, [start], *, echo_start=True)

      It's an implementation of the scan higher order function with
      more features than ``itertools.accumulate`` (the ``start`` and
      the keyword-only ``echo_start`` parameters) and consistent to
      the ``functools.reduce`` function signature.


Tell me, how is that possible at all?
-------------------------------------

Magic! Some people say that's bytecode manipulation, but isn't that all the
same?


Installing
----------

You can either use pip:

.. code-block:: shell

  # From PyPI
  pip install pyscanprev

  # From GitHub master branch
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

It's not only about code aesthetics or readability, but also about
pattern memorization: knowledge about the scan abstraction
and about the Python language is probably
not enough for one to remember that structure.

As ``func`` in the previous example was essentially ``operator.add``, let's do
the same cumulative sum with ``itertools.accumulate`` (Python 3.2+):

.. code-block:: python

  >>> from itertools import accumulate
  >>> list(accumulate(range(5)))
  [0, 1, 3, 6, 10]

It seems the same, but here the first zero output is the
``next(iter(range(5)))``,
not the result of a sum or any other ``func`` for that matter (i.e., it
doesn't depend on ``func`` at all). To be really equivalent to the
3-for-sections list comprehension above, it would need to be something like:

.. code-block:: python

  >>> list(accumulate([0, 0, 1, 2, 3, 4]))[1:]
  [0, 1, 3, 6, 10]

We had to prepend ``0`` to ``range(5)``. What's going on here is that
``accumulate`` returns a generator that yields the values::

  [i0, i0+i1, i0+i1+i2, i0+i1+i2+i3, i0+i1+i2+i3+i4, ...]

Where "i\ :sub:`n`" is the n-th value from the ``iterable`` input.
Every step obviously re-uses the previous step result instead
of summing all the previous inputs again,
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
whose last update was in 2006. Besides the distinction between
non-strict and "prime"/strict counterparts, it mimics all the
`4 scan and 4 fold Haskell functions`_\ , including their names
and their parameter order. The ``functional.scanl1`` and
the ``itertools.accumulate`` functions are almost the
same, the difference is that ``scanl1`` needs the function to be the first
argument and it isn't optional. On the other hand, ``functional.scanl`` needs
an extra "start" parameter. Both functions return a generator:

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

Python ``functools.reduce``, ``functional.foldl`` and
``functional.foldl1``, as fold/reduce implementations,
share a core idea: they return the last value of the scan
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
