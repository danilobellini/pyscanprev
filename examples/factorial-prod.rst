Factorial and Multiplication
============================

This example requires:

.. code-block:: python

  >>> from pyscanprev import enable_scan, last

Actually, these are simple reduce/fold examples, not scan examples,
but PyScanPrev enables us to write them as generator expressions.


Factorial
---------

.. code-block:: python

  >>> @enable_scan("prev")
  ... def factorial(n):
  ...     return last(prev * k for k in range(2, n + 1) or [1])

The whole logic is in the:

.. code-block:: python

  last(prev * k for k in range(2, n + 1) or [1])

Where the ``or [1]`` makes the result valid for ``n in [0, 1]``.
The first ``prev`` value is actually the first input, so using
the ``last`` function requires at least one element in the
input iterable (the ``range(2, n + 1) or [1]`` in this case).

.. code-block:: python

  >>> factorial(0)
  1
  >>> factorial(1)
  1
  >>> factorial(2)
  2
  >>> factorial(3)
  6
  >>> factorial(4)
  24
  >>> factorial(5)
  120
  >>> factorial(6)
  720
  >>> factorial(7)
  5040


Multiplication / Product of a sequence
--------------------------------------

When the ``last`` is called and the sequence is empty, it would
raise ``StopIteration`` like ``next`` would do on an empty
iterator.

.. code-block:: python

  >>> @enable_scan("prev")
  ... def prod(iterable):
  ...     try:
  ...         return last(prev * k for k in iterable)
  ...     except StopIteration:
  ...         return 1

Let's evaluate some products:

.. code-block:: python

  >>> prod([2, 3, 4, 5, 6, 7])
  5040
  >>> prod([])
  1
  >>> prod(range(3, -6, -2)) # 3 * 1 * -1 * -3 * -5
  -45
  >>> prod(x ** 2 for x in [5, 1.2, 0.12, 1.1])
  0.627264
  >>> prod({"!", 2, 3}) # "!" * 2 * 3, the order doesn't matter
  '!!!!!!'
