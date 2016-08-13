itertools.accumulate documentation examples
===========================================

The following examples requires:

.. code-block:: python

  >>> from itertools import accumulate, repeat
  >>> import operator

As of the day this text was written, the `itertools.accumulate`_
documentation had these examples of running product, running maximum,
amortization tables and chaotic logistic map:

.. code-block:: python

  >>> data = [3, 4, 6, 2, 1, 9, 0, 7, 5, 8]
  >>> list(accumulate(data, operator.mul))     # running product
  [3, 12, 72, 144, 144, 1296, 0, 0, 0, 0]
  >>> list(accumulate(data, max))              # running maximum
  [3, 4, 6, 6, 6, 9, 9, 9, 9, 9]

  # Amortize a 5% loan of 1000 with 4 annual payments of 90
  >>> cashflows = [1000, -90, -90, -90, -90]
  >>> list(accumulate(cashflows, lambda bal, pmt: bal*1.05 + pmt))
  [1000, 960.0, 918.0, 873.9000000000001, 827.5950000000001]

  # Chaotic recurrence relation https://en.wikipedia.org/wiki/Logistic_map
  >>> logistic_map = lambda x, _:  r * x * (1 - x)
  >>> r = 3.8
  >>> x0 = 0.4
  >>> inputs = repeat(x0, 36)     # only the initial value is used
  >>> [format(x, '.2f') for x in accumulate(inputs, logistic_map)]
  ['0.40', '0.91', '0.30', '0.81', '0.60', '0.92', '0.29', '0.79', '0.63',
   '0.88', '0.39', '0.90', '0.33', '0.84', '0.52', '0.95', '0.18', '0.57',
   '0.93', '0.25', '0.71', '0.79', '0.63', '0.88', '0.39', '0.91', '0.32',
   '0.83', '0.54', '0.95', '0.20', '0.60', '0.91', '0.30', '0.80', '0.60']

.. _`itertools.accumulate`:
  https://docs.python.org/3/library/itertools.html#itertools.accumulate


The same with PyScanPrev
------------------------

Go ahead and compare.

.. code-block:: python

  >>> from pyscanprev import enable_scan
  >>> @enable_scan("prev")
  ... def gen():
  ...     yield [prev * item for item in data]
  ...     yield [max(prev, item) for item in data]
  ...     yield [prev * 1.05 + pmt for pmt in cashflows]
  ...     yield [format(x, '.2f') for x in [r * prev * (1 - prev)
  ...                                       for unused in inputs]]
  >>> g = gen()

  >>> data = [3, 4, 6, 2, 1, 9, 0, 7, 5, 8]
  >>> next(g) # [prev * item for item in data] # running product
  [3, 12, 72, 144, 144, 1296, 0, 0, 0, 0]
  >>> next(g) # [max(prev, item) for item in data] # running maximum
  [3, 4, 6, 6, 6, 9, 9, 9, 9, 9]

  # Amortize a 5% loan of 1000 with 4 annual payments of 90
  >>> cashflows = [1000, -90, -90, -90, -90]
  >>> next(g) # [prev * 1.05 + pmt for pmt in cashflows]
  [1000, 960.0, 918.0, 873.9000000000001, 827.5950000000001]

  # Chaotic recurrence relation https://en.wikipedia.org/wiki/Logistic_map
  >>> r = 3.8
  >>> x0 = 0.4
  >>> inputs = repeat(x0, 36)     # only the initial value is used
  >>> next(g) # [format(x, '.2f') for x in [r * prev * (1-prev)
  ...         #                             for unused in inputs]]
  ['0.40', '0.91', '0.30', '0.81', '0.60', '0.92', '0.29', '0.79', '0.63',
   '0.88', '0.39', '0.90', '0.33', '0.84', '0.52', '0.95', '0.18', '0.57',
   '0.93', '0.25', '0.71', '0.79', '0.63', '0.88', '0.39', '0.91', '0.32',
   '0.83', '0.54', '0.95', '0.20', '0.60', '0.91', '0.30', '0.80', '0.60']
