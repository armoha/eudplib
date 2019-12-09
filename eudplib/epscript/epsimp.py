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

from importlib.machinery import FileFinder, SourceFileLoader

from .epscompile import epsCompile
from eudplib.localize import _
from eudplib.utils import EPError
import os
import sys
import re
from bisect import bisect_right

import types


lineno_regex = re.compile(b" *# \\(Line (\\d+)\\) .+")


def modifyCodeLineno(codeobj, codeMap):
    co_lnotab = codeobj.co_lnotab
    co_firstlineno = codeobj.co_firstlineno

    # Reconstruct code data
    new_lnotab = []
    currentLine = co_firstlineno
    currentMappedLine = codeMap(currentLine)
    for i in range(0, len(co_lnotab), 2):
        bytecodeLen, lineAdvance = co_lnotab[i : i + 2]
        nextLine = currentLine + lineAdvance
        nextMappedLine = codeMap(nextLine)
        newLineAdvance = nextMappedLine - currentMappedLine
        while newLineAdvance >= 0xFF:
            new_lnotab.append(bytes([0, 0xFF]))
            newLineAdvance -= 0xFF
        new_lnotab.append(bytes([bytecodeLen, newLineAdvance]))
        currentLine = nextLine
        currentMappedLine = nextMappedLine

    # For code objects
    new_co_consts = []
    for c in codeobj.co_consts:
        if isinstance(c, types.CodeType):
            c = modifyCodeLineno(c, codeMap)
        new_co_consts.append(c)

    codeobj = types.CodeType(
        codeobj.co_argcount,
        codeobj.co_posonlyargcount,  # python 3.8 support (See PEP 570)
        codeobj.co_kwonlyargcount,
        codeobj.co_nlocals,
        codeobj.co_stacksize,
        codeobj.co_flags,
        codeobj.co_code,
        tuple(new_co_consts),
        codeobj.co_names,
        codeobj.co_varnames,
        codeobj.co_filename,
        codeobj.co_name,
        codeMap(co_firstlineno),  # codeobj.co_firstlineno,
        b"".join(new_lnotab),  # codeobj.co_lnotab,
        codeobj.co_freevars,
        codeobj.co_cellvars,
    )

    return codeobj


class EPSLoader(SourceFileLoader):
    def get_data(self, path):
        """Return the data from path as raw bytes."""
        fileData = open(path, "rb").read()
        if path.endswith(".pyc") or path.endswith(".pyo"):
            return fileData
        print(_('[epScript] Compiling "{}"...').format(os.path.relpath(path)))
        compiled = epsCompile(path, fileData)
        if compiled is None:
            raise EPError(_(" - Compiled failed for {}").format(path))
        dirname, filename = os.path.split(path)
        epsdir = os.path.join(dirname, "__epspy__")
        try:
            if not os.path.isdir(epsdir):
                os.mkdir(epsdir)
            ofname = os.path.splitext(filename)[0] + ".py"
            ofname = os.path.join(epsdir, ofname)
            with open(ofname, "w", encoding="utf-8") as file:
                file.write(compiled.decode("utf-8"))
        except OSError:
            pass

        return compiled

    def source_to_code(self, data, path, *, _optimize=-1):
        codeobj = super().source_to_code(data, path, _optimize=_optimize)

        # Read lines from code data
        codeLine = [0]
        codeMap = [0]
        data = data.replace(b"\r\n", b"\n")
        for lineno, line in enumerate(data.split(b"\n")):
            match = lineno_regex.match(line)
            if match:
                codeLine.append(lineno + 1)
                codeMap.append(int(match.group(1)))

        # Reconstruct code data
        def lineMapper(line):
            return codeMap[bisect_right(codeLine, line) - 1]

        codeobj = modifyCodeLineno(codeobj, lineMapper)
        return codeobj


class EPSFinder:
    def __init__(self):
        self._finderCache = {}

    def _getFinder(self, path):
        try:
            return self._finderCache[path]
        except KeyError:
            self._finderCache[path] = FileFinder(path, (EPSLoader, [".eps"]))
            return self._finderCache[path]

    def find_spec(self, fullname, path, target=None):
        if path is None:
            path = sys.path
        for pathEntry in path:
            finder = self._getFinder(pathEntry)
            spec = finder.find_spec(fullname)
            if spec is None:
                continue
            return spec


sys.meta_path.append(EPSFinder())
