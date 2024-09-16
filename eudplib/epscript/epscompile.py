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


libeps = CDLL(find_data_file(_libfile, __file__))
libeps.compileString.argtypes = [c_char_p, c_char_p]
libeps.compileString.restype = c_void_p
libeps.freeCompiledResult.argtypes = [c_void_p]
libeps.setDebugMode.argtypes = [c_int]
libeps.getErrorCount.argtypes = []
libeps.getErrorCount.restype = c_int
libeps.registerPlibConstants.argtypes = [c_char_p]
libeps.registerPyKeywords.argtypes = [c_char_p]
libeps.registerPyBuiltins.argtypes = [c_char_p]


def _set_eps_globals(global_list):
    global_list_c = b"\0".join(u2b(g) for g in global_list) + b"\0"
    libeps.registerPlibConstants(global_list_c)


def _set_py_keywords(keyword_list):
    keyword_list_c = b"\0".join(u2b(g) for g in keyword_list) + b"\0"
    libeps.registerPyKeywords(keyword_list_c)


def _set_py_builtins(builtin_list):
    builtin_list_c = b"\0".join(u2b(g) for g in builtin_list) + b"\0"
    libeps.registerPyBuiltins(builtin_list_c)


def epsCompile(filename, b_code):  # noqa: N802
    filename = u2b(filename)
    output = libeps.compileString(filename, b_code)
    if not output or libeps.getErrorCount():
        return None
    output_str = c_char_p(output).value
    libeps.freeCompiledResult(output)
    return output_str


def EPS_SetDebug(b):  # noqa: N802
    libeps.setDebugMode(b)
