# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import platform
from ctypes import CDLL, c_char_p, c_int, c_void_p

from ..utils import find_data_file, u2b

_libfile = {
    "Linux": "libepScriptLib.so",  # Linux
    "Windows": "libepScriptLib.dll",  # Windows
    "Darwin": "libepScriptLib.dylib",  # Mac
}[platform.system()]

# The library is loaded lazily on first use, so importing eudplib does not
# require libepScriptLib to be present (it may not have been built for the
# current platform yet). Registrations made before the first load are applied
# once the library is available.
_libeps = None

_pending_plib_constants = None
_pending_py_keywords = None
_pending_py_builtins = None


def _load_lib():
    global _libeps
    if _libeps is not None:
        return _libeps
    path = find_data_file(_libfile, __file__)
    try:
        lib = CDLL(path)
    except OSError as exc:
        raise ImportError(
            f"Could not load the epScript library {path!r}. Build libepScriptLib "
            "for your platform and place it in eudplib/epscript/ (see the "
            "'Building from source' section of the README)."
        ) from exc
    lib.compileString.argtypes = [c_char_p, c_char_p]
    lib.compileString.restype = c_void_p
    lib.freeCompiledResult.argtypes = [c_void_p]
    lib.setDebugMode.argtypes = [c_int]
    lib.getErrorCount.argtypes = []
    lib.getErrorCount.restype = c_int
    lib.registerPlibConstants.argtypes = [c_char_p]
    lib.registerPyKeywords.argtypes = [c_char_p]
    lib.registerPyBuiltins.argtypes = [c_char_p]
    if _pending_plib_constants is not None:
        lib.registerPlibConstants(_pending_plib_constants)
    if _pending_py_keywords is not None:
        lib.registerPyKeywords(_pending_py_keywords)
    if _pending_py_builtins is not None:
        lib.registerPyBuiltins(_pending_py_builtins)
    _libeps = lib
    return lib


def _set_eps_globals(global_list):
    global _pending_plib_constants
    global_list_c = b"\0".join(u2b(g) for g in global_list) + b"\0"
    _pending_plib_constants = global_list_c
    if _libeps is not None:
        _libeps.registerPlibConstants(global_list_c)


def _set_py_keywords(keyword_list):
    global _pending_py_keywords
    keyword_list_c = b"\0".join(u2b(g) for g in keyword_list) + b"\0"
    _pending_py_keywords = keyword_list_c
    if _libeps is not None:
        _libeps.registerPyKeywords(keyword_list_c)


def _set_py_builtins(builtin_list):
    global _pending_py_builtins
    builtin_list_c = b"\0".join(u2b(g) for g in builtin_list) + b"\0"
    _pending_py_builtins = builtin_list_c
    if _libeps is not None:
        _libeps.registerPyBuiltins(builtin_list_c)


def epsCompile(filename, b_code):  # noqa: N802
    lib = _load_lib()
    filename = u2b(filename)
    output = lib.compileString(filename, b_code)
    if not output or lib.getErrorCount():
        return None
    output_str = c_char_p(output).value
    lib.freeCompiledResult(output)
    return output_str


def EPS_SetDebug(b):  # noqa: N802
    _load_lib().setDebugMode(b)
