Single Pole Lowpass IIR filter
==============================

In this example we'll use these:

.. code-block:: python

  >>> from audiolazy import lowpass, pi, z, saw_table, sHz
  >>> from pyscanprev import enable_scan, prepend
  >>> from hipsterplot import plot

Say we want an IIR (Infinite Impulse Response) LTI (Linear Time
Invariant) digital filter, e.g. a lowpass filter whose cutoff
frequency is about pi/30 rad/sample (i.e., 735 Hz when the sample
rate is at 44100 samples per second). After some math, an
approximation for a single pole filter would be:

.. code-block:: python

  >>> radius = 0.9

This filter can be described by its Z-Transform equation::

  >>> lowpass(pi / 30)
       0.0993371
  -------------------
  1 - 0.900663 * z^-1

Let's store this filter with our radius for further comparison:

.. code-block:: python

  >>> lzfilt = (1 - radius) / (1 - radius * z ** -1)

In the time domain, it can be expressed as::

  y[n] = (1 - radius) * x[n] + radius * y[n - 1]

Let's create the filter using PyScanPrev:

.. code-block:: python

  >>> @enable_scan("yn_1")
  ... def pspfilt(data):
  ...     return [(1 - radius) * xn + radius * yn_1 for xn in data]

Say we have some square way signal at 315 Hz (pi/70 rad/sample),
let's get 6.35 milliseconds (280 samples) from that signal:

.. code-block:: python

  >>> data = [0] * 70 + [1] * 70 + [0] * 70 + [1] * 70
  >>> plot(data, num_x_chars=56)
      0.9667               ##############              ##############
      0.9000
      0.8333
      0.7667
      0.7000
      0.6333
      0.5667
      0.5000
      0.4333
      0.3667
      0.3000
      0.2333
      0.1667
      0.1000
      0.0333 ##############              ##############

Comparing the results for both filters:

.. code-block:: python

  >>> lzresult = list(lzfilt(data))
  >>> pspresult = pspfilt(prepend(0, data))[1:]
  >>> lzresult == pspresult
  True
  >>> plot(pspresult, num_x_chars=56)
      0.9661                    #########                   #########
      0.8994                  .#         .                .#
      0.8328                  |          .                |
      0.7662                 |                           |
      0.6996                 :           .               :
      0.6329                :            .              :
      0.5663                .            .              .
      0.4997                :             :             :
      0.4331               .              .            .
      0.3664               .              :            .
      0.2998               .               :           .
      0.2332                               |
      0.1666               .                |          .
      0.0999               .                .#         .
      0.0333 ##############                   #########

Applying it on a 150 Hz (pi/147 rad/sample) sawtooth wave:

.. code-block:: python

  >>> s, Hz = sHz(rate=44100)
  >>> saw_data = saw_table(150*Hz).take(0.01*s)
  >>> plot(saw_data, num_x_chars=56)
      0.9268                                   .##|
      0.7939                                 ###
      0.6610                              .##:
      0.5281                            ###
      0.3953                         .##:
      0.2624                       ###
      0.1295                    .##|
     -0.0034                  ###                                  :#
     -0.1363                ##|                                  ###
     -0.2691             ###                                  .##|
     -0.4020           ##|                                  ###
     -0.5349        |##                                  .##|
     -0.6678      ##|                                  |##
     -0.8007   |##                                  .##|
     -0.9336 ##|                                  ###
  >>> plot(pspfilt(saw_data), num_x_chars=56)
      0.8676                                    ##|
      0.7388                                 |##  .
      0.6100                               ##|    .
      0.4812                            :##.
      0.3524                          ###         .
      0.2236                       .##:           .
      0.0948                     |##              ..
     -0.0340                   ##|                 .                #
     -0.1628                |##                    .              ##|
     -0.2916              ###                      :           |##
     -0.4204           :##.                        |         ###
     -0.5492         ###                            |     :##.
     -0.6780      .##|                              #:  ###
     -0.8068    |##                                  ###.
     -0.9356 ###|

Other linear filters can be created with the combination of IIR/FIR
filters and their results. FIR (Finite Impulse Response) filters don't
require knowledge about the previous inputs, these would be done with
common list comprehensions or AudioLazy ``ZFilter`` objects like
``1 - z ** -1``.

The `State-space model`_ PyScanPrev example has more signal
processing / control theory models, including another LTI filtering
example.

.. _`State-space model`: state-space.rst
