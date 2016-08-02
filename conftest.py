"""
Py.test configuration to fix functional.scanl1 to work on Python 3.
"""
def pytest_configure(config):
    """
    Py.test hook for fixing functional.scanl1 to call the ``__next__``
    method instead of the Python2-specific ``next`` method.
    """
    import functional, inspect
    exec(inspect.getsource(functional.scanl1).replace("next", "__next__"),
         functional.__dict__, functional.__dict__)
