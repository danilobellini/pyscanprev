Fibonacci
=========

This example requires:

.. code-block:: python

  >>> from pyscanprev import enable_scan, last
  >>> from itertools import repeat, takewhile
  >>> from operator import itemgetter


Definition
----------

Fibonacci is defined as::

  fib(0) = 0
  fib(1) = 1
  fib(n) = fib(n - 1) + fib(n - 2)

That recursive definition requires the 2 previous output values. To
use scan with a memory of a single past value, we'll need to store a
pair of values on each iteration instead of a single number. Let's
make a scan that yields pairs like this on each iteration::

  fib(n - 1), fib(n)

The previous value is always::

  fib(n - 2), fib(n - 1)

Which should start on ``(0, 1)``. The scan should just yield the
second memory value (``fib(n - 1)``) and their sum (definition of
``fib(n)`` for ``n > 1``).


From 0 to n
-----------

.. code-block:: python

  >>> @enable_scan("prev_pair")
  ... def fib_up_to(n):
  ...     iterable = repeat((0, 1), n)
  ...     pairs = ((prev_pair[1], sum(prev_pair)) for el in iterable)
  ...     return [0] + [pair[1] for pair in pairs]

This Fibonacci implementation returns a list with n + 1 items::

  [fib(0), fib(1), ..., fib(n - 1), fib(n)]

Let's see the results for some small input values:

.. code-block:: python

  >>> fib_up_to(0)
  [0]
  >>> fib_up_to(1)
  [0, 1]
  >>> fib_up_to(3)
  [0, 1, 1, 2]
  >>> fib_up_to(5)
  [0, 1, 1, 2, 3, 5]
  >>> fib_up_to(16)
  [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]


Single value
------------

Perhaps all we want is the last value, not the whole sequence.

.. code-block:: python

  >>> @enable_scan("prev_pair")
  ... def fib(n):
  ...     iterable = repeat((0, 1), n)
  ...     pairs = ((prev_pair[1], sum(prev_pair)) for el in iterable)
  ...     return 0 if n == 0 else last(pairs)[1]

We can compare this implementation with the previous results:

.. code-block:: python

  >>> fib(5)
  5
  >>> fib(8)
  21
  >>> fib(16)
  987
  >>> fib_up_to(50) == [fib(k) for k in range(51)]
  True

This should work fine (and fast) for numbers that are quite large:

.. code-block:: python

  >>> fib(217)
  1001919737325604309473206237898433933302481297
  >>> fib(227)
  123227981463641240980692501505442003148737643593
  >>> fib(303)
  941390895042587567453271223806288165311401367715034229502159202


Endless generator
-----------------

.. code-block:: python

  >>> @enable_scan("prev_pair")
  ... def fibg():
  ...     yield 0
  ...     iterable = repeat((0, 1))
  ...     pairs = ((prev_pair[1], sum(prev_pair)) for el in iterable)
  ...     yield from map(itemgetter(1), pairs)

Is there a last Fibonacci number?

.. code-block:: python

  >>> g = fibg()
  >>> next(g), next(g), next(g), next(g)
  (0, 1, 1, 2)
  >>> next(g), next(g), next(g), next(g)
  (3, 5, 8, 13)
  >>> next(g), next(g), next(g), next(g)
  (21, 34, 55, 89)
  >>> next(g), next(g), next(g), next(g)
  (144, 233, 377, 610)
  >>> next(g), next(g), next(g), next(g)
  (987, 1597, 2584, 4181)

This example is quite simple to implement imperatively with a
Python generator function without PyScanPrev:

.. code-block:: python

  >>> def fibg_nopsp():
  ...     yield 0
  ...     a, b = 0, 1
  ...     while True:
  ...         yield b
  ...         a, b = b, a + b

And these implementations should behave the same way:

.. code-block:: python

  >>> def generate_limited(gen_func, value=1e7):
  ...     return list(takewhile(lambda x: x < value, gen_func()))
  >>> generate_limited(fibg) == generate_limited(fibg_nopsp)
  True

With PyScanPrev, the ``pairs`` variable is always defined by the same
generator expression in every Fibonacci implementation shown here.
That's also the only place where the the ``prev_pair`` variable
appears.
