# -*- coding: utf-8 -*-
"""
Tools for searching bytecode for key statements which indicate need for
additional resources e.g. data file, package metadata.
"""

import dis
import re
from types import CodeType


def _instruction_to_regex(x: str):
    """Get a regex-escaped opcode byte from its human readable name."""
    if x not in dis.opname:  # pragma: no cover
        # These opcodes are available only in Python >=3.7.
        # For our purposes, these aliases will do.
        if x == "LOAD_METHOD":
            x = "LOAD_ATTR"
        elif x == "CALL_METHOD":
            x = "CALL_FUNCTION"
    return re.escape(bytes([dis.opmap[x]]))


class BytecodeRegex(object):
    def __init__(self, pattern, flags=re.VERBOSE | re.DOTALL):
        assert isinstance(pattern, bytes)
        self.pattern = pattern

        # Anything wrapped in backticks needs to be replaced with
        # regex-escaped opcodes.
        pattern = re.sub(
            rb"`(\w+)`",
            lambda m: _instruction_to_regex(m[1].decode()),
            pattern,
        )
        self.re = re.compile(pattern, flags=flags)
        self.match = self.re.match
        self.search = self.re.search
        self.finditer = self.re.finditer
        self.findall = self.re.findall

    def __repr__(self):
        return f"{type(self).__name__}(rb'''{self.pattern.decode()}''')"


# language=PythonVerboseRegExp
_call_global_bytecode = BytecodeRegex(rb"""
    # Matches `global_function('some', 'constant', 'arguments')`.

    # Load the global function.
    # In code with >256 of names, this may require extended name references.
    ((?:`EXTENDED_ARG`.)*
     (?:`LOAD_NAME`|`LOAD_GLOBAL`).)

    # For foo.bar.whizz(), the above is the 'foo', below is the 'bar.whizz'.    
    ((?:(?:`EXTENDED_ARG`.)*
     (?:`LOAD_METHOD`|`LOAD_ATTR`).)*)

    # Load however many arguments it takes. These (for now) must all be
    # constants. Again, code with >256 constants may need extended enumeration.
    ((?:(?:`EXTENDED_ARG`.)*
     `LOAD_CONST`.)*)

    # Call the function. The parameter is the argument count (which may also be
    # >256).
    ((?:`EXTENDED_ARG`.)*
     (?:`CALL_FUNCTION`|`CALL_METHOD`).)

""")

# language=PythonVerboseRegExp
_extended_arg_bytecode = BytecodeRegex(rb"""(

    # Arbitrary number of EXTENDED_ARG pairs. 
    (?:`EXTENDED_ARG`.)*

    # Followed by some other instruction (usually a LOAD).
    [^`EXTENDED_ARG`].

)""")


def _extended_arguments(extended_args: bytes):
    """Unpack the (extended) integer used to reference names or constants.

    The input should be a bytecode snippet of the following form::

        EXTENDED_ARG    ?      # Repeated 0-4 times.
        LOAD_xxx        ?      # Any of LOAD_NAME/LOAD_CONST/LOAD_METHOD/...

    Each ? byte combined together gives the number we want.

    """
    return int.from_bytes(extended_args[1::2], "big")


def _parse_loads(raw: bytes):
    return map(_extended_arguments, _extended_arg_bytecode.findall(raw))


def function_calls(code: CodeType):
    """Scan a code object for all function calls on strictly constant arguments.
    """
    match: re.Match
    out = []

    for match in _call_global_bytecode.finditer(code.co_code):
        function_root, methods, args, arg_count = match.groups()

        # For foo():
        #   `function_root` contains 'foo' and `methods` is empty.
        # For foo.bar.whizz():
        #   `function_root` contains 'foo' and `methods` contains the rest.
        function_root = code.co_names[_extended_arguments(function_root)]
        methods = [code.co_names[i] for i in _parse_loads(methods)]
        function = ".".join([function_root] + methods)

        args = [code.co_consts[i] for i in _parse_loads(args)]
        arg_count = _extended_arguments(arg_count)

        if arg_count != len(args):
            # This happens if there are variable arguments or keyword arguments.
            # Bail out in either case.
            continue

        out.append((function, args))

    return out


def search_recursively(search: callable, code: CodeType, _memo=None) -> dict:
    if _memo is None:
        _memo = {}
    if code not in _memo:
        _memo[code] = search(code)
        for const in code.co_consts:
            if isinstance(const, CodeType):
                search_recursively(search, const, _memo)
    return _memo
