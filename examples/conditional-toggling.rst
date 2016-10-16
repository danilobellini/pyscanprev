Conditional Toggling Example
============================

Sometimes you want to make something that simply alternates, toggles
or cycles in a well-defined sequence of values, for example to
alternate upper and lowercase characters:

.. code-block:: python

  >>> an_example = "an example"
  >>> "".join(ch.upper() if idx & 1 else ch.lower()
  ...         for idx, ch in enumerate(an_example))
  'aN ExAmPlE'

The same could have been done with ``idx % 2`` or ``idx % 2 == 1``
instead of ``idx & 1``, but any of these would miss an important
point: the whitespace counts, and the result isn't really
cycling/alternating between a lower and an uppercase character.
There's an ``"N E"`` in that sequence, adjacent letters that are both
uppercase because of a whitespace in between. How to "skip" that
whitespace when toggling the case?


Solution with PyScanPrev
------------------------

To model the "state" for toggling, one would need to know:

- The previous state, i.e., whether the previous letter character was
  an upper or a lowercase character;
- Whether the new character is a letter that should toggle the case
  state, or anything else that would just bypass.

That's where the scan could help. The solution for a switcher would be
an xor (or "different") operation between the state and a flag that
tells us if the state should toggle or not, i.e.:

============= ================= =========
Current state Should it toggle? New state
============= ================= =========
False         False             False
False         True              True
True          False             True
True          True              False
============= ================= =========

Where the state is just a flag that tells the character case, and it
should toggle only when the new character is a letter. The ``cases``
generator in the solution below has the case state for each character
in a given message:

.. code-block:: python

  >>> from pyscanprev import enable_scan, prepend
  >>> @enable_scan("prev")
  ... def alternate(msg, start=True):
  ...     """
  ...     Alternate upper and lowercase letters in the given message,
  ...     starting with an uppercase character if start is True.
  ...     """
  ...     cases = (prev != ch.isalpha() for ch in prepend(start, msg))
  ...     methods = ([str.lower, str.upper][case] for case in cases)
  ...     return "".join(meth(ch) for meth, ch in zip(methods, msg))

Using it:

.. code-block:: python

  >>> alternate(an_example)
  'An ExAmPlE'

  >>> alternate(an_example, start=False)
  'aN eXaMpLe'

  >>> alternate("Alternating cases, ignoring OTHER characters", False)
  'aLtErNaTiNg CaSeS, iGnOrInG oThEr ChArAcTeRs'


Solution with itertools.accumulate or pyscanprev.scan
-----------------------------------------------------

Let's alternate the upper/lower case in:

.. code-block:: python

  >>> my_msg = "This is a dancing sentence"

Based on the ``alternate`` function, one can use the
``itertools.accumulate`` function instead of a generator expression to
obtain the ``cases`` iterable, but that still requires the
``pyscanprev.prepend`` function as the ``accumulate`` doesn't have a
``start`` parameter and in this example the output data type
(booleans) and the input data type (single character strings) aren't
the same:

.. code-block:: python

  >>> from itertools import accumulate
  >>> cases = accumulate(prepend(True, my_msg),
  ...                    lambda prev, ch: prev != ch.isalpha())
  >>> methods = ([str.lower, str.upper][case] for case in cases)
  >>> "".join(meth(ch) for meth, ch in zip(methods, my_msg))
  'ThIs Is A dAnCiNg SeNtEnCe'

To avoid using the ``prepend`` function, you should use
``[start] + list(my_msg)`` or something alike.

In this case, using ``pyscanprev.scan`` instead of
``itertools.accumulate`` would be simpler, as it already has a
``start`` parameter.

.. code-block:: python

  >>> from pyscanprev import scan
  >>> cases = scan(lambda prev, ch: prev != ch.isalpha(),
  ...              my_msg, start=True)
  >>> methods = ([str.lower, str.upper][case] for case in cases)
  >>> "".join(meth(ch) for meth, ch in zip(methods, my_msg))
  'ThIs Is A dAnCiNg SeNtEnCe'


Solution with reduce and without PyScanPrev
-------------------------------------------

The same idea used when implementing the solution with PyScanPrev can
be used with a rather cryptic reduce command with some slight changes
(e.g. using ``+`` instead of ``str.join``):

.. code-block:: python

  >>> from functools import reduce
  >>> reduce(lambda s, ch: (s[0] + [ch.lower(), ch.upper()][s[1]],
  ...                       s[1] != ch.isalpha()),
  ...        an_example,
  ...        ("", True)
  ...       )[0]
  'An ExAmPlE'

There are several other ways to solve this, e.g.:

.. code-block:: python

  >>> "".join([chl, chu][c]
  ...         for chl, chu, c
  ...          in zip(my_msg.lower(),
  ...                 my_msg.upper(),
  ...                 reduce(lambda s, isalpha: s + [s[-1] ^ isalpha],
  ...                        [ch.isalpha() for ch in my_msg],
  ...                        [0])))
  'tHiS iS a DaNcInG sEnTeNcE'

You can store some parts of these "oneliner" declarative solutions in
variables with expressive names, but even if you do so, implementing
scan with ``functools.reduce`` would require this pattern or something
analogous to it:

.. code-block:: python

  reduce(lambda history, new_data:
             history + [func(history[-1], new_data)],
         input_data, [start])

Which isn't that easy to grasp even for a simple "accumulator"
function ``func`` like the bitwise xor, unless abstracted away in
another function like ``pyscanprev.scan``.
