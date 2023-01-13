#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

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


def setEpsGlobals(globalList):
    globalList_C = b"\0".join(u2b(g) for g in globalList) + b"\0"
    libeps.registerPlibConstants(globalList_C)


def setPyKeywords(keywordList):
    keywordList_C = b"\0".join(u2b(g) for g in keywordList) + b"\0"
    libeps.registerPyKeywords(keywordList_C)


def setPyBuiltins(builtinList):
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
