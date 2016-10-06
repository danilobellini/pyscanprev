IIR filter
==========

In this example we'll use these:

.. code-block:: python

  >>> from audiolazy import lowpass, pi, z
  >>> from pyscanprev import enable_scan, prepend

Say we want an IIR (Infinite Impulse Response) LTI (Linear Time
Invariant) digital filter, e.g. a lowpass filter whose cutoff
frequency is about pi/30 rad/sample (i.e., 735 Hz when the sample
rate is at 44100 samples per second). After some math, an
approximation for a single pole filter would be:

.. code-block:: python

  >>> radius = 0.9

This filter can be described by its Z-Transform equation:

.. code-block:: python

  >>> lowpass(pi / 30)
       0.0993371
  -------------------
  1 - 0.900663 * z^-1

Let's store this filter with our radius, for further comparison:

.. code-block:: python

  >>> lzfilt = (1 - radius) / (1 - radius * z ** -1)

In the time domain, it can be expressed as::

  y[n] = (1 - radius) * x[n] + radius * y[n - 1]

Let's create the filter using PyScanPrev:

.. code-block:: python

  >>> @enable_scan("yn")
  ... def pspfilt(data):
  ...     return [(1 - radius) * xn + radius * yn for xn in data]

Say we have some square way signal at 220.5 Hz, let's get some
milliseconds from that signal:

.. code-block:: python

  >>> data = [0] * 100 + [1] * 100 + [0] * 100 + [1] * 100

Comparing the results for both filters:

.. code-block:: python

  >>> lzresult = list(lzfilt(data))
  >>> pspresult = pspfilt(prepend(0, data))[1:]
  >>> lzresult == pspresult
  True
