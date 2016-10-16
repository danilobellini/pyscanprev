State-space model
=================

This example requires:

.. code-block:: python

  >>> from pyscanprev import enable_scan, prepend
  >>> import itertools
  >>> from numpy import mat
  >>> from hipsterplot import plot
  >>> from audiolazy import z

The most sophisticated/interesting examples are the mass-spring-damper
"bucket" models at the end of this text, which includes a SHM (Simple
Harmonic Motion) example and a leaking bucket example (a time varying
model). It's perhaps more interesting to see them as a motivation
before reading/understanding how their model were built.


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


LTI IIR filter example
----------------------

Say we have a LTI (Linear Time Invariant) IIR (Infinite Impulse
Response) digital filter that can be expressed as this equation::

  y[k] = 2⋅u[k] - u[k-1] + u[k-2] + y[k-1] - y[k-2]/2

This filter can be expressed by its Z transform (classical method)
transfer function and rewritten as a parallel filter (i.e., a sum
of filter transfer functions)::

                     -1     -2             -1             -2
         Y(z)   2 - z  + 2⋅z              z              z
  H(z) = ──── = ────────────── = 2 + ──────────── + ────────────
         U(z)        -1   -2              -1   -2        -1   -2
                1 - z  + z           1 - z  + z     1 - z  + z
                         ───                  ───            ───
                          2                    2              2

         Y(z)       F(z)   F(z)  -1       F(z)   G(z)
  H(z) = ──── = 2 + ──── + ────⋅z   = 2 + ──── + ────
         U(z)       U(z)   U(z)           U(z)   U(z)

Going back to the time domain, that's::

  y[k] = 2⋅u[k] + f[k] + g[k]
  f[k] = u[k-1] + f[k-1] - f[k-2]/2
  g[k] = f[k-1]

Or::

  y[k] = 2⋅u[k] + f[k] + g[k]
  f[k+1] = u[k] + f[k] - g[k]/2
  g[k+1] = f[k]

Then our matrices are::

      ⎡1 -1/2⎤        ⎡1⎤
  A = ⎢      ⎥    B = ⎢ ⎥    C = [1 1]    D = [2]
      ⎣1   0 ⎦        ⎣0⎦

Let's simulate that for a "triangle" signal as our input:

.. code-block:: python

  >>> triangle = [1, 2, 3, 4, 5, 4, 3, 2, 1, 0]
  >>> model = ltiss(A = mat([[1, -1/2],
  ...                        [1,  0  ]]),
  ...               B = mat([1, 0]).T,
  ...               C = mat([1, 1]),
  ...               D = mat(2.0))
  >>> result = list(model(triangle))
  >>> [yk[0, 0] for yk in result]
  [2.0, 5.0, 10.0, 16.5, 23.5, 26.25, 26.5, 22.375, 15.125, 6.9375]

One can compare this with the AudioLazy result for the classic
modeling method:

.. code-block:: python

  >>> filt = (2 - z**-1 + 2*z**-2) / (1 - z**-1 + z**-2/2)
  >>> list(filt(triangle))
  [2.0, 5.0, 10.0, 16.5, 23.5, 26.25, 26.5, 22.375, 15.125, 6.9375]

A simpler LTI IIR filter example can be seen in the
`Single pole lowpass`_ PyScanPrev example.

.. _`Single pole lowpass`: iir-filter.rst


Linear time invariant mass-spring-damper state-space model
----------------------------------------------------------

**Continuous time bucket-spring-damper model**

There's a spring and damper system fixed on the ceiling, and we're
going to put a bucket on it::

  ════════════╦═══╦═══╦═════════════
            __│   ╽   │__
           (__⎠╲  ┃  ╱⎝__)
            ___╱  ┃  ╲___
           (__╱╲  ┃  ╱╲__)
            ___╱ ⎥┃⎢ ╲___
           (__╱╲ ⎥┃⎢ ╱╲__)
            ___╱ ⎥┃⎢ ╲___
           (__╱╲ ⎥┻⎢ ╱╲__)
            ___╱ ⎥ ⎢ ╲___
           (__╱╲ ⎥ ⎢ ╱╲__)
            ___╱ ⎥ ⎢ ╲___
           (__╱⎞ ⎥ ⎢ ⎛╲__)
               │ ╰┬╯ │
               ╘══╪══╛
                  ┆
              .-=≈╪≈=-.
             ╱    ╰╯   ╲
            /           \
           ⎥             ⎢
           |.-'¯‾‾‾‾‾¯'-.|
           ⎢ ~∽´˜˜‾˜˜`∽~ ⎥
           ⎢`-._______.-´⎥
           ⎢             ⎥
           ⎢             ⎥
           ⎢             ⎥
           \             /
            `-._______.-´

The force equation for that system is::

  m * a(t) = - m * g - c * v(t) - k * h(t)

Where:

- ``t`` is the time
- ``m`` is the bucket mass including its contents
- ``g`` is the gravity acceleration
- ``c`` is the damping coefficient
- ``k`` is the spring stiffness constant (joined)
- ``a(t) = v̇(t)`` is the bucket acceleration
- ``v(t) = ḣ(t)`` is the bucket velocity
- ``h(t)`` is the bucket height

Starting in ``h(0) = 0``, where the spring force (Hooke's law) is
still zero. That's when the bucket is attached to the springs-damper
system and left to oscillate.

Everything could be seen as a function of time, and the dot above
some symbols denotes the derivative with respect to the time.
Let's define the state vector as a pair including the height and the
velocity. If we want to see the bucket trajectory as the system
output, this system would then be described by an equation like::

  ⎡ḣ(t)⎤   ⎡  0     1 ⎤ ⎡h(t)⎤   ⎡ 0⎤
  ⎢    ⎥ = ⎢          ⎥⋅⎢    ⎥ + ⎢  ⎥
  ⎣v̇(t)⎦   ⎣-k/m  -c/m⎦ ⎣v(t)⎦   ⎣-g⎦

               ⎡h(t)⎤
  y(t) = [1 0]⋅⎢    ⎥
               ⎣v(t)⎦

That's a linear time invariant state model, with the continuous
time formulation::

  ẋ(t) = Aa⋅x(t) + Ba⋅u(t)
  y(t) = Ca⋅x(t) + Da⋅u(t)

         ⎡h(t)⎤
  x(t) = ⎢    ⎥
         ⎣v(t)⎦

Where ``u(t)`` is the Heaviside step function (i.e., ``1`` for
``k > 0``) and::

       ⎡  0     1 ⎤         ⎡ 0⎤
  Aa = ⎢          ⎥    Ba = ⎢  ⎥    Ca = [1 0]    Da = [0]
       ⎣-k/m  -c/m⎦         ⎣-g⎦

**Converting the system from continuous time to discrete time**

The state derivative can be seen as::

  ẋ(t) = lim   x(t + T) - x(t)
         T->0  ───────────────
                      T

Suppose a sampling period of ``T`` where the system is seen only
for ``t = k⋅T``, where ``k`` is a time index. If T is small, that
ratio is an approximation to the continuous derivative, and we can
convert the state equation to::

  ẋ(t) = Aa⋅x(t) + Ba⋅u(t)
  x(t + T) - x(t) = Aa⋅T⋅x(t) + Ba⋅T⋅u(t)
  x(t + T) = (I + Aa⋅T)⋅x(t) + Ba⋅T⋅u(t)
  x((k + 1)⋅T) = (I + Aa⋅T)⋅x(k⋅T) + Ba⋅T⋅u(k⋅T)
  x[k + 1] = (I + Aa⋅T)⋅x[k] + Ba⋅T⋅u[k]

And the output equation::

  y(t) = Ca⋅x(t) + Da⋅u(t)
  y(k⋅T) = Ca⋅x(k⋅T) + Da⋅u(k⋅T)
  y[k] = Ca⋅x[k] + Da⋅u[k]

Where ``I`` is the n x n eye matrix, and the square bracket notation
``x[k]`` is a convenient way to write ``x(k⋅T)``. That gives us a
mapping from the continuous time matrices to our digital sampled
system matrices::

  A = I + Aa⋅T
  B = Ba⋅T
  C = Ca
  D = Da

**Simulation with PyScanPrev**

Then, our matrices are::

      ⎡   1       T   ⎤        ⎡  0 ⎤
  A = ⎢               ⎥    B = ⎢    ⎥    C = [1 0]    D = [0]
      ⎣-k⋅T/m  1-c⋅T/m⎦        ⎣-g⋅T⎦

Let's simulate it using the previously defined ``ltiss`` function for
some actual values in SI (Système international d'unités):

.. code-block:: python

  >>> m = 5     # kilogram
  >>> c = 2.5   # newton * second / metre, or kilogram / second
  >>> k = 119.2 # newton / metre, or kilogram / second ** 2
  >>> g = 9.8   # metre / second ** 2
  >>> end = 5.7       # second
  >>> num_k = 2850    # samples
  >>> T = end / num_k # second/sample
  >>> model = ltiss(
  ...     A = mat([[   1  ,   T    ],
  ...              [-k*T/m, 1-c*T/m]]),
  ...     B = mat([[0], [-g*T]]),
  ...     C = mat([[1, 0]]),
  ...     D = 0)
  >>> result = list(model(
  ...     u = [1] * num_k, # Step function
  ...     x0 = 0,
  ... ))
  >>> plot([yk[0, 0] for yk in result], num_x_chars=57)
     -0.0255 #|
     -0.0766  #
     -0.1277  #         ###|
     -0.1788  ##        #  #         ###
     -0.2299   #       ##  #|        # ##         ###
     -0.2810   #       #    #       ##  #|       ## ##         ###
     -0.3321   #:      #    #       #    #       #   ##       ## ##
     -0.3832    #     ##    ##     ##    #|     ##    #      ##   |#
     -0.4343    #     #      #     #      #     #     |#    ##     ##
     -0.4854    #     #      #    ##      ##   #       ##  ##       ##
     -0.5365    ##   ##      :#   #        #  ##        ####
     -0.5876     #   #        #  ##        ####
     -0.6387     #   #        ##:#
     -0.6898     ## #|         ##
     -0.7409      ###


Linear time varying state-space model
-------------------------------------

Say we have a leaking bucket attached to a spring and damper system
fixed on the ceiling like the previous example::

  ════════════╦═══╦═══╦═════════════
            __│   ╽   │__
           (__⎠╲  ┃  ╱⎝__)
            ___╱  ┃  ╲___
           (__╱╲  ┃  ╱╲__)
            ___╱ ⎥┃⎢ ╲___
           (__╱╲ ⎥┃⎢ ╱╲__)
            ___╱ ⎥┃⎢ ╲___
           (__╱╲ ⎥┻⎢ ╱╲__)
            ___╱ ⎥ ⎢ ╲___
           (__╱╲ ⎥ ⎢ ╱╲__)
            ___╱ ⎥ ⎢ ╲___
           (__╱⎞ ⎥ ⎢ ⎛╲__)
               │ ╰┬╯ │
               ╘══╪══╛
                  ┆
              .-=≈╪≈=-.
             ╱    ╰╯   ╲
            /           \
           ⎥             ⎢
           |.-'¯‾‾‾‾‾¯'-.|
           ⎢ ~∽´˜˜‾˜˜`∽~ ⎥
           ⎢`-._______.-´⎥
           ⎢             ⎥
           ⎢             ⎥
           ⎢           ◉ ⎥
           \            ▚/
            `-._______.-´▌
                         ▚
                         ▐
                         ´▌
                         .▌
                         ´▐`
                         ,▐:
                          ▐:
                         ''▌.
                         ,:▌;

Whose mass is linearly decaying at a rate ``r``::

  m(t) = max(0, (ma - r⋅t)) + mb

Where:

- ``ma`` is the starting water mass
- ``mb`` is the empty bucket mass
- ``r`` is the rate

Now the ``A`` matrix isn't constant, but every equation used in the
previous example are still the same. Simulating that with PyScanPrev
gives us:

.. code-block:: python

  >>> ma = 4.8 # kilogram
  >>> mb = 0.2 # kilogram
  >>> r = 0.42 # kilogram / second
  >>> m = (max(0, (ma - r * k * T)) + mb for k in itertools.count(1))
  >>> ltv_result = [yk[0, 0] for yk in ltvss(
  ...     A = (mat([[   1   ,   T     ],
  ...               [-k*T/mk, 1-c*T/mk]]) for mk in m),
  ...     B = itertools.repeat(mat([[0], [-g*T]])),
  ...     C = itertools.repeat(mat([[1, 0]])),
  ...     D = itertools.repeat(0),
  ...     u = [1] * num_k, # Step function
  ...     x0 = mat([0, 0]).T,
  ... )]
  >>> plot(ltv_result, num_x_chars=57)
     -0.0247 #:
     -0.0740  #         ###
     -0.1234  #         # #         ###         #
     -0.1727  ##       ##  #       ## ##       ####      ####      ###
     -0.2221   #       #   #       #   #      #|  #     ##  ##    #:
     -0.2714   #       #   ##     ##   ##    ##   ##    #    ## |#:
     -0.3208   #      #|    #     #     #    #     ##  #      ###
     -0.3702   .#     #     #     #     ##  ##      ####
     -0.4195    #     #     |#   ##      #  #
     -0.4689    #    ##      #   #       ####
     -0.5182    ##   #       ## ##
     -0.5676     #   #        ###
     -0.6169     #  ##         #
     -0.6663     ## #
     -0.7156      ###

The same can be done with a dedicated function:

.. code-block:: python

  >>> @enable_scan("prev")
  ... def leaking_bucket(ma, mb, r, k, c, g, T, num_k, **unused):
  ...     m = (max(0, (ma - r * k * T)) + mb for k in range(1, num_k))
  ...     A = (mat([[   1   ,   T     ],
  ...               [-k*T/mk, 1-c*T/mk]]) for mk in m)
  ...     B = mat([0, -g*T]).T
  ...     x = (Ak * prev + B for Ak in prepend(mat([0, 0]).T, A))
  ...     return [xk[0, 0] for xk in x]
  >>> leaking_bucket(**locals()) == ltv_result
  True

Can you write the ``m[k]`` using PyScanPrev instead of
``itertools.count`` or ``range``?
