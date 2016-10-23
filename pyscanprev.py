# By Danilo J. S. Bellini
import types, collections, bytecode

__version__ = "0.1.0"

_EMPTY = object()

def code_mix(code, **changes):
    """
    Creates a new code object based on another, as a copy where the given
    keyword parameters are seen as attributes to be modified. See
    code_mix.keys for the keyword list.
    """
    args = (changes.get(arg, getattr(code, arg)) for arg in code_mix.keys)
    return types.CodeType(*args)

code_mix.keys = [
    "co_argcount", "co_kwonlyargcount", "co_nlocals", "co_stacksize",
    "co_flags", "co_code", "co_consts", "co_names", "co_varnames",
    "co_filename", "co_name", "co_firstlineno", "co_lnotab", "co_freevars",
    "co_cellvars"
]


def function_mix(func, **changes):
    """
    Creates a new function object based on another, as a copy where the given
    keyword attributes are modified. See function_mix.keys for the keyword
    list.

    Info: The valid keyword arguments are the keys, but the function
    attributes are actually the dunders (double underscored prefix and suffix)
    of the keys, not the keys themselves.
    """
    args = (changes.get(arg, getattr(func, "__%s__" % arg))
            for arg in function_mix.keys)
    return types.FunctionType(*args)

function_mix.keys = ["code", "globals", "name", "defaults", "closure"]


def _enable_scan_single_bytecode(code, name):
    """
    Part of the ``_enable_scan`` that applies the scan behavior on a single
    given list/set comprehension or generator expression code.
    """
    bc = bytecode.Bytecode.from_code(code)
    Instr = bytecode.Instr

    # Updates LOAD_GLOBAL to LOAD_FAST when arg is name
    for instr in bc:
        if isinstance(instr, Instr) \
        and instr.name == "LOAD_GLOBAL" and instr.arg == name:
            instr.set("LOAD_FAST", name)

    # Some needed information from the first/main FOR_ITER and the heading
    # "filter" part of the generator expression or list/set comprehension
    for_idx = next(idx for idx, instr in enumerate(bc)
                       if getattr(instr, "name", None) == "FOR_ITER")
    for_instr = bc[for_idx]
    begin_label_idx = for_idx - 1
    try:
        filter_last_idx = last(idx for idx, instr in enumerate(bc)
                                   if isinstance(instr, Instr)
                                   and instr.is_cond_jump()
                                   and instr.arg == begin_label_idx)
    except StopIteration:
        filter_last_idx = for_idx

    # Adds the block before the loop (i.e., first label) to append/add/yield
    # the first input directly from FOR_ITER and save the first "prev"
    # accordingly
    heading_instructions = [("DUP_TOP",),
                            ("STORE_FAST", name)] + {
        "<listcomp>": [("LIST_APPEND", 2)],
        "<setcomp>":  [("SET_ADD", 2)],
        "<genexpr>":  [("YIELD_VALUE",),
                       ("POP_TOP",)]
    }[bc.name]
    bc[begin_label_idx:begin_label_idx] = (
        [instr.copy() for instr in bc[for_idx:filter_last_idx + 1]] +
        [Instr(*args) for args in heading_instructions]
    )

    # Adds ending block that stores the result to prev before a new iteration
    loop_instructions = ["SET_ADD", "LIST_APPEND", "YIELD_VALUE"]
    ending_idx = next(-idx for idx, instr in enumerate(reversed(bc), 1)
                           if isinstance(instr, Instr)
                           and instr.name in loop_instructions)
    ending_instructions = [("DUP_TOP",),
                           ("STORE_FAST", name)]
    bc[ending_idx:ending_idx] = \
        [Instr(*args) for args in ending_instructions]

    return bc.to_code()


def _enable_scan(code, name):
    """
    Recursive function that enables the scan on generator expressions and
    list/set comprehensions. See the ``enable_scan`` function docs for more
    information.
    """
    if name in code.co_names \
    and code.co_name in {"<listcomp>", "<setcomp>", "<genexpr>"}:
        code = _enable_scan_single_bytecode(code, name)

    consts = list(code.co_consts)
    for idx, subcode in enumerate(code.co_consts):
        if isinstance(subcode, types.CodeType):
            consts[idx] = _enable_scan(subcode, name)

    if consts == list(code.co_consts):
        return code
    return code_mix(code, co_consts=tuple(consts))


def enable_scan(name):
    """
    Parametrized decorator that enables the scan behavior on
    generators/lists/sets.

    Changes every list/set comprehension and generator expression that has
    in its body the variable with the given name but doesn't iterate on it,
    returning a modified version of the given code.

    The scan behavior is:

    - The first output value (append/add/yield) is the first input value;
    - The previous result is stored in a variable with the given ``name``.

    Example
    -------

    >>> @enable_scan("p")
    ... def powerset(iterable):
    ...     return [set.union(p, {item}) for item in prepend(set(), iterable)]
    >>> powerset([1, 2, 3])
    [set(), {1}, {1, 2}, {1, 2, 3}]
    >>> powerset("Test")
    [set(), {'T'}, {'T', 'e'}, {'T', 'e', 's'}, {'T', 'e', 's', 't'}]
    """
    def decorator(func):
        return function_mix(func, code=_enable_scan(func.__code__, name))
    return decorator


def last(iterable):
    """A next(iterable) that drops everything but the last item"""
    it = iter(iterable)
    item = next(it)
    for item in it:
        pass
    return item


def prepend(value, iterable):
    """
    Generator for an iterable that has to yield one extra value
    BEFORE iterating over its contents.

    >>> next(prepend(2, []))
    2
    >>> list(prepend(True, range(5)))
    [True, 0, 1, 2, 3, 4]
    """
    yield value
    yield from iterable


def scan(func, iterable, start=_EMPTY, *, echo_start=True):
    """
    Scan higher-order function.

    The first 3 positional arguments are alike to the ``functools.reduce``
    signature. This function accepts an extra optional ``echo_start``
    parameter that controls whether the first value should be in the output.
    """
    it = iter(iterable)
    if start is _EMPTY:
        start = next(it)
    if echo_start:
        yield start
    for item in it:
        start = func(start, item)
        yield start
