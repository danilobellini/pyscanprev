State-space model
=================

This example requires:

.. code-block:: python

  >>> from pyscanprev import enable_scan, prepend
  >>> import itertools
  >>> from numpy import mat


Theory
------

The state-space model is a modern control method for describing,
analysing and designing systems in control engineering. The
linear time varying discrete state model is::

  x[k + 1] = A[k]⋅x[k] + B[k]⋅u[k]
  y[k]     = C[k]⋅x[k] + D[k]⋅u[k]

Where:

- ``⋅`` is the [matrix] multiplication operator
- ``k`` is the time index
- ``x[k]`` is the system state vector (n X 1)
- ``u[k]`` is the input vector (m X 1)
- ``y[k]`` is the output vector (p X 1)
- ``A[k]`` is the system matrix (n X n)
- ``B[k]`` is the control matrix (n X m)
- ``C[k]`` is the output matrix (p X n)
- ``D[k]`` is the feed-forward matrix (p X m)

These are the the MIMO (Multiple Input Multiple Output) equations
as described by Wilson J. Rugh in his "Linear System Theory" book,
chapter 20, p. 383. Usually only the time invariant model (i.e., the
ones with constant matrices A, B, C and D) are discussed, as there is
a wide knowledge on how to get information about the system using
these matrices (e.g. controlability, observability, transition
matrix, stability criteria, converting to/from the classical model,
etc.) and also and wide range of applications where these can be
used (mechanics, electronics, economics, social sciences, etc.).


Implementation
--------------

PyScanPrev can be used to write the time-invariant model
in a straightforward manner with generator expressions:

.. code-block:: python

  >>> def ltiss(A, B, C, D):
  ...     @enable_scan("p")
  ...     def model_function(u, x0=0):
  ...         u1, u2 = itertools.tee(u, 2)
  ...         x = (A * p  + B * uk for     uk in prepend(x0, u1))
  ...         y = (C * xk + D * uk for xk, uk in zip(x, u2))
  ...         return y
  ...     return model_function

The same can be said about the time varying model:

.. code-block:: python

  >>> @enable_scan("p")
  ... def ltvss(A, B, C, D, u, x0=0):
  ...     Ak, Bk, Ck, Dk = map(iter, [A, B, C, D])
  ...     u1, u2 = itertools.tee(u, 2)
  ...     x = (next(Ak) * p + next(Bk) * uk for uk in prepend(x0, u1))
  ...     y = (next(Ck) * xk + next(Dk) * uk for xk, uk in zip(x, u2))
  ...     return y

The ``*`` (mul) operator was used instead of the ``@`` (matmul)
operator to let this example work in Python 3.4, but that means that
only scalars and ``numpy.mat`` objects can be used with these
functions, not ``numpy.array`` instances.

Actually, the name ``p`` could have been ``xk``, but that would look
confusing in the ``y`` generator expression, as it has ``xk`` as a
target.


Accumulator example
-------------------

.. code-block:: python

  >>> input_data = [1, 1, 1, 1, 1, 5, -2, -2, -3, -3]

The aforementioned ``ltiss`` function works either with numbers
(instead of 1x1 matrices) and Numpy matrices (not arrays), but you
should care about the result type when using matrices. Let's see a
simple accumulator using both approaches. Without matrices:

.. code-block:: python

  >>> matrixless_model = ltiss(1, 1, 1, 1)
  >>> list(matrixless_model(input_data))
  [1, 2, 3, 4, 5, 10, 8, 6, 3, 0]

With matrices (``D`` could have been ``mat([[1]])`` as well):

.. code-block:: python

  >>> model = ltiss(A = mat([[1, 0],
  ...                        [0, 1]]),
  ...               B = mat([[1],
  ...                        [1]]),
  ...               C = mat([[1, 0]]),
  ...               D = 1)
  >>> result = list(model(input_data, x0=mat([[-1],
  ...                                         [ 0]])))
  >>> all(yk.shape == (1, 1) for yk in result) # mat([[value]])
  True
  >>> [yk[0, 0] for yk in result]
  [0, 1, 2, 3, 4, 9, 7, 5, 2, -1]

The ``ltvss`` function has a similar behavior, but requires iterables
on Numpy matrices or numbers, and there's no "model" partial
application as the time varying matrices should match the index of
the input, and it would be strange to use the same matrices more
than once. One can use ``itertools.repeat`` when the input isn't
varying:

.. code-block:: python

  >>> list(ltvss(
  ...     A = itertools.repeat(1),
  ...     B = itertools.repeat(1),
  ...     C = itertools.repeat(1),
  ...     D = itertools.repeat(1),
  ...     u = input_data,
  ...     x0 = -1,
  ... ))
  [0, 1, 2, 3, 4, 9, 7, 5, 2, -1]
  >>> [yk[0, 0] for yk in ltvss(
  ...     A = itertools.repeat(mat([[1, 0],
  ...                               [0, 1]])),
  ...     B = itertools.repeat(mat([[1],
  ...                               [1]])),
  ...     C = itertools.repeat(mat([[1, 0]])),
  ...     D = itertools.repeat(1),
  ...     u = input_data,
  ...     x0 = mat([[0],
  ...               [0]]),
  ... )]
  [1, 2, 3, 4, 5, 10, 8, 6, 3, 0]
