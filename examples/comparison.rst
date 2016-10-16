Comparison Example
==================

The goal of this example is to show how to do the same scan/accumulate
and fold/reduce operations using:

- The PyScanPrev package;
- The Python standard library (``itertools.accumulate`` and
  ``functools.reduce``);
- 3-for-sections comprehensions.

For the remaining, I'm assuming that we have imported everything:

.. code-block:: python

  >>> from pyscanprev import enable_scan, last, prepend, scan
  >>> import itertools, functools, operator


Enabling PyScanPrev on comprehensions
-------------------------------------

This package allows us to:

.. code-block:: python

  >>> @enable_scan("prev")
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

The basic idea in that decorator is that it changes the expressions to ensure
a variable with the given name (``prev`` in this example) always have the
previous output value inside list/set comprehensions and generator expressions
internal loops (i.e., the last values appended/added/yielded). It also
appends/adds/yields the first input (target variable value). That's somehow
needed as any expression with ``prev`` has no meaning before there is a
``prev``, and that keeps the input iterable length equal to the output iterable
length, besides being the behavior of other scan implementations.

But how would we do that without this package? And with ``pyscanprev.scan``?
Are there other scan implementations?


Cumulative sum with list comprehension
--------------------------------------

The first example is a cumulative sum using a list comprehension.

.. code-block:: python

  >>> g = gen()
  >>> next(g) # [prev + el for el in range(15)]
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]

That's actually this::

  [0, 0+1, 0+1+2, 0+1+2+3, 0+1+2+3+4, ...]

The same result can be obtained by using either ``itertools.accumulate``
(Python 3.2+) or ``pyscanprev.scan``:

.. code-block:: python

  >>> list(itertools.accumulate(range(15)))
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]
  >>> list(scan(operator.add, range(15)))
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]

As that's exactly what they do. The first zero isn't the result of any sum,
and ``accumulate`` returns a generator function. These are the same:

.. code-block:: python

  (prev + el for el in iterable) # PyScanPrev, assuming in a enabled context
  itertools.accumulate(iterable) # Python 3.2+ standard library
  scan(operator.add, iterable)   # PyScanPrev scan, reminds functional.reduce

There's a way to do a cumulative sum with a 3-for-sections list comprehension.
`README.rst`_ rationale section contains some description about how this
behavior.

.. code-block:: python

  >>> start, *remaining = range(15)
  >>> [start] + [prev for prev in [start]
  ...                 for el in remaining
  ...                 for prev in [prev + el]]
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]

The ``[start]`` prepend was there because this structure doesn't "echo" it to
the output. As summing zero doesn't change the result in this particular case,
we can:

.. code-block:: python

  >>> [prev for prev in [0]
  ...           for el in range(15)
  ...           for prev in [prev + el]]
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]

Which isn't the same for a general function, as it's applying a scan to a
``[0, 0, 1, 2, 3, ..., 14]`` input and then getting rid from the first output.
When using this kind of solution either you have an identity/neutral element,
or you don't care about echoing the first value to the result. There's an
``echo_start`` keyword argument for ``scan`` that, together with its optional
``start`` argument, allows doing the same:

.. code-block:: python

  >>> list(scan(operator.add, range(15), start=0, echo_start=False))
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]

Obviously, you can also do the same appending imperatively within a for loop:

.. code-block:: python

  >>> start, *remaining = range(15)
  >>> result = [start]
  >>> for el in remaining:
  ...     result.append(result[-1] + el)
  ...
  >>> result
  [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]


Scan with set comprehension
---------------------------

Let's se a case where the function isn't a simple cumulative sum. Why not a
product of squared values?

.. code-block:: python

  >>> next(g) # {prev * x ** 2 for x in [1, -2, 3, 2]}
  {1, 4, 36, 144}

That's like the list comprehension, but applied to a set, showing there's no
``-1`` indexing being done at all.

Again, ``pyscanprev.scan`` and ``itertools.accumulate`` can give us
alternative approaches. Now, we'll use the second ``accumulate`` argument
(Python 3.3+), which defaults to ``operator.add``:

.. code-block:: python

  >>> set(itertools.accumulate([1, -2, 3, 2], lambda prev, x: prev * x ** 2))
  {1, 4, 36, 144}
  >>> set(scan(lambda prev, x: prev * x ** 2, [1, -2, 3, 2]))
  {1, 4, 36, 144}

This extra argument is some binary operation callable, and it's needed for
``scan``, but appears reversed with the iterable. These are the same:

.. code-block:: python

  (func(prev, x) for x in iterable)    # PyScanPrev in an enabled context
  itertools.accumulate(iterable, func) # Python 3.3+ standard library
  scan(func, iterable)                 # PyScanPrev scan with implicit start

Just as before, be careful that the first value 1 isn't a square. The result
is::

  {1, 1 * (-2)**2, 1 * (-2)**2 * 3**2, 1 * (-2)**2 * 3**2 * 2**2}

And there's also a solution using a 3-for-sections set comprehension:

.. code-block:: python

  >>> start, *remaining = [1, -2, 3, 2]
  >>> set.union({start},
  ...           {prev for prev in [start]
  ...                 for x in remaining
  ...                 for prev in [prev * x ** 2]})
  {1, 4, 36, 144}

Getting rid from the union is still possible as ``1`` is the identity:

.. code-block:: python

  >>> set.union({prev for prev in [1]
  ...                 for x in [1, -2, 3, 2]
  ...                 for prev in [prev * x ** 2]})
  {1, 4, 36, 144}

But in this case there's a ``1 * 1`` being done to result in that 1. The same
can be done with ``scan`` using a command to avoid "echoing" the start to the
result:

.. code-block:: python

  >>> set(scan(lambda prev, x: prev * x ** 2,
  ...          [1, -2, 3, 2], echo_start=False))
  {4, 36, 144}
  >>> set(scan(lambda prev, x: prev * x ** 2,
  ...          [1, -2, 3, 2],
  ...          start=1, echo_start=False))
  {1, 4, 36, 144}

A for loop imperative approach would be:

.. code-block:: python

  >>> start, *remaining = [1, -2, 3, 2]
  >>> result = {start}
  >>> for x in remaining:
  ...     start *= x ** 2
  ...     result.add(start)
  >>> result
  {1, 4, 36, 144}


Fold/reduce with last + generator expression scan
-------------------------------------------------

Folding is just getting the last value from a scan. So, with the
``pyscanprev.last`` function you can get the last value from the
previous example:

.. code-block:: python

  >>> next(g) # last(prev * x ** 2 for x in [1, -2, 3, 2])
  144

You can call ``last`` on a ``itertools.accumulate`` generator result:

.. code-block:: python

  >>> last(itertools.accumulate([1, -2, 3, 2],
  ...                           lambda prev, x: prev * x ** 2))
  144

On Python 2 there were a built-in called ``reduce``. Python 3 moved it to the
``functools`` module. You can use the ``functools.reduce`` directly:

.. code-block:: python

  >>> functools.reduce(lambda prev, x: prev * x ** 2, [1, -2, 3, 2])
  144

Notice the reversed parameter order when compared to ``accumulate``. Does it
remind you of the ``pyscanprev.scan`` function?

.. code-block:: python

  >>> last(scan(lambda prev, x: prev * x ** 2, [1, -2, 3, 2]))
  144
  >>> last(scan(lambda prev, x: prev * x ** 2,
  ...           [1, -2, 3, 2], echo_start=False))
  144

We don't need to care about the starting value to get the last one, so we
don't need to prepend ``start`` to the result:

.. code-block:: python

  >>> start, *remaining = [1, -2, 3, 2]
  >>> [prev for prev in [start]
  ...       for x in remaining
  ...       for prev in [prev * x ** 2]
  ... ][-1]
  144

But that's a list comprehension, not a generator. A mixed solution with a
generator using the fact that ``1`` is the identity here would be:

.. code-block:: python

  >>> last(prev for prev in [1]
  ...           for x in [1, -2, 3, 2]
  ...           for prev in [prev * x ** 2])
  144

As that generator expression can't be indexed, to replace the
``pyscanprev.last`` call you would need either to cast/store its values on a
structure like a list/tuple, or to rewrite the last function behavior.
There's no direct way to do that with a generator.

This for loop version is simpler than the previous ones:

.. code-block:: python

  >>> result, *remaining = [1, -2, 3, 2]
  >>> for x in remaining:
  ...     result *= x ** 2
  >>> result
  144


Prepend scan with start value (explicit)
----------------------------------------

Let's do something a little bit different, with a custom starting value for
the iterable.

.. code-block:: python

  >>> next(g) # [el - abs(prev) for el in prepend(15, [5, 6, 7, 8])]
  [15, -10, -4, 3, 5]

This is simply::

  15, 5 - abs(-15), 6 - abs(5 - abs(-15)), 7 - abs(6 - abs(5 - abs(-15))), ...

Or::

  15, 5 - abs(-15), 6 - abs(-10), 7 - abs(-4), 8 - abs(3)

As ``itertools.accumulate`` doesn't have a start parameter, you can use the
``pyscanprev.prepend`` there as well.

.. code-block:: python

  >>> list(itertools.accumulate(prepend(15, [5, 6, 7, 8]),
  ...                           lambda prev, el: el - abs(prev)))
  [15, -10, -4, 3, 5]

Did you know the first lambda argument is prev?

There's a 3rd parameter for ``scan``, a starting value like the 3rd ``reduce``
parameter. We already used it, but as a keyword argument:

.. code-block:: python

  >>> list(scan(lambda prev, el: el - abs(prev), [5, 6, 7, 8], 15))
  [15, -10, -4, 3, 5]
  >>> list(scan(func = lambda prev, el: el - abs(prev),
  ...           iterable = [5, 6, 7, 8],
  ...           start = 15))
  [15, -10, -4, 3, 5]

There's also a possible solution with ``functools.reduce``:

.. code-block:: python

  >>> functools.reduce(lambda h, el: h + [el - abs(h[-1])],
  ...                  [5, 6, 7, 8], [15])
  [15, -10, -4, 3, 5]

The function was changed, but that gives us a scan from a fold. These are
about the same:

.. code-block:: python

  # Python standard library, works on Python 2
  functools.reduce(lambda h, x: h + [func(h[-1], x)], iterable, [start])

  # PyScanPrev scan function
  list(scan(func, iterable, start))

A 3-for-sections solution:

.. code-block:: python

  >>> [15] + [prev for prev in [15]
  ...              for el in [5, 6, 7, 8]
  ...              for prev in [el - abs(prev)]]
  [15, -10, -4, 3, 5]

Or using the fact that the identity element is zero:

.. code-block:: python

  >>> [prev for prev in [0]
  ...       for el in prepend(15, [5, 6, 7, 8])
  ...       for prev in [el - abs(prev)]]
  [15, -10, -4, 3, 5]

Obviously for a list you can prepend the value directly to it, the prepend
function is mainly intended to be used with a generator or an general unknown
iterable.

.. code-block:: python

  >>> def some_generator():
  ...     yield 5
  ...     yield 6
  ...     yield 7
  ...     yield 8
  >>> [prev for prev in [0]
  ...       for el in prepend(15, some_generator())
  ...       for prev in [el - abs(prev)]]
  [15, -10, -4, 3, 5]

These 3-for-section loops are possible because Python allows using the same
variable twice in the multiple for loop parts "cartesian product". But would
you really do that? Do you prefer that over the other solutions given here?

For the sake of completeness, a for loop solution is:

.. code-block:: python

  >>> start = 15
  >>> result = {start}
  >>> for el in some_generator(): # Or the list [5, 6, 7, 8]
  ...     start = el - abs(start)
  ...     result.add(start)
  >>> result
  {-10, -4, 3, 5, 15}
