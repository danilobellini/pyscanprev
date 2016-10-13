"""
Py.test configuration to fix functional.scanl1 to work on Python 3,
to fix hipsterplot.plot to print without whitespaces and to define
the docstring display hook function for pytest-doctest-custom.
"""
from IPython.lib.pretty import pretty

def repr4test(val):
    if type(val) is list and all(type(x) is str and len(x) == 4 for x in val):
        return "\n".join("".join(blk) for blk in zip(*[iter(repr(val))]*72))
    return pretty(val)

def pytest_configure(config):
    """
    Py.test hook for fixing functional.scanl1 to call the ``__next__``
    method instead of the Python2-specific ``next`` method, and to fix
    the hipsterplot "print" function to strip trailing whitespaces.
    """
    import functional, inspect, hipsterplot
    exec(inspect.getsource(functional.scanl1).replace("next", "__next__"),
         functional.__dict__, functional.__dict__)
    hipsterplot.print = lambda data: print(data.rstrip())
