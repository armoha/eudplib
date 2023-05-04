#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import platform
from ctypes import CDLL, c_char_p, c_int, c_void_p

from eudplib.utils import find_data_file, u2b

libFile = {
    "Linux": "libepScriptLib.so",  # Linux
    "Windows": "libepScriptLib.dll",  # Windows
    "Darwin": "libepScriptLib.dylib",  # Mac
}[platform.system()]


libeps = CDLL(find_data_file(libFile, __file__))
libeps.compileString.argtypes = [c_char_p, c_char_p]
libeps.compileString.restype = c_void_p
libeps.freeCompiledResult.argtypes = [c_void_p]
libeps.setDebugMode.argtypes = [c_int]
libeps.getErrorCount.argtypes = []
libeps.getErrorCount.restype = c_int
libeps.registerPlibConstants.argtypes = [c_char_p]
libeps.registerPyKeywords.argtypes = [c_char_p]
libeps.registerPyBuiltins.argtypes = [c_char_p]


def _setEpsGlobals(globalList):
    globalList_C = b"\0".join(u2b(g) for g in globalList) + b"\0"
    libeps.registerPlibConstants(globalList_C)


def _setPyKeywords(keywordList):
    keywordList_C = b"\0".join(u2b(g) for g in keywordList) + b"\0"
    libeps.registerPyKeywords(keywordList_C)


def _setPyBuiltins(builtinList):
    builtinList_C = b"\0".join(u2b(g) for g in builtinList) + b"\0"
    libeps.registerPyBuiltins(builtinList_C)


def epsCompile(filename, bCode):
    filename = u2b(filename)
    output = libeps.compileString(filename, bCode)
    if not output or libeps.getErrorCount():
        return None
    outputStr = c_char_p(output).value
    libeps.freeCompiledResult(output)
    return outputStr


def EPS_SetDebug(b):
    libeps.setDebugMode(b)
