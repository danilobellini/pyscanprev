"""
Py.test configuration for using a custom printer function for doctests.
"""
import sys, functools

def temp_replace(obj, attr_name, value):
    """
    Returns a decorator that replaces obj.attr = value before calling the
    wrapped function and restores obj.attr afterwards.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            backup = getattr(obj, attr_name)
            setattr(obj, attr_name, value)
            result = func(*args, **kwargs)
            setattr(obj, attr_name, backup)
            return result
        return wrapper
    return decorator

def printer(value):
    if isinstance(value, set) and value:
        print(repr(sorted(value))[1:-1].join("{}"))
    elif value is not None:
        print(value)

def pytest_configure(config):
    """
    Py.test hook for changing doctest.DocTestRunner so that the displayhook
    calls the given printer method.
    """
    import doctest

    enable_printer = temp_replace(sys, "__displayhook__", printer)
    doctest.DocTestRunner.run = enable_printer(doctest.DocTestRunner.run)
    # As the public method doctest.DocTestRunner.run replaces sys.displayhook
    # by sys.__displayhook__, we could also had changed "displayhook" on the
    # _DocTestRunner__run protected method
