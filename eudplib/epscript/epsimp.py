#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os
import re
import sys
import types
from importlib.machinery import FileFinder, SourceFileLoader

from eudplib.bindings._rust import epscript
from eudplib.localize import _
from eudplib.utils import EPError

from .epscompile import epsCompile

lineno_regex = re.compile(b" *# \\(Line (\\d+)\\) (.+)")
is_scdb_map = False


def IsSCDBMap():  # noqa: N802
    return is_scdb_map


class EPSLoader(SourceFileLoader):
    def create_module(self, spec):
        module_name = spec.name
        module = types.ModuleType(module_name)
        module.__name__ = module_name
        module.__loader__ = self
        sys.modules[module_name] = module
        return module

    def get_data(self, path):
        """Return the data from path as raw bytes."""
        global is_scdb_map
        file_data = open(path, "rb").read()
        if path.endswith(".pyc") or path.endswith(".pyo"):
            return file_data
        if "SCDB.eps" in os.path.relpath(path):
            is_scdb_map = True
        print(_('[epScript] Compiling "{}"...').format(os.path.relpath(path)))
        compiled = epsCompile(path, file_data)
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
        if sys.version_info >= (3, 11):
            linetable = epscript.generate_linetable(
                data, codeobj.co_linetable, codeobj.co_positions()
            )
            codeobj.replace(co_linetable=linetable)
        else:
            raise NotImplementedError
        return codeobj


class EPSFinder:
    def __init__(self):
        self._finderCache = {}

    def _get_finder(self, path):
        try:
            return self._finderCache[path]
        except KeyError:
            self._finderCache[path] = FileFinder(path, (EPSLoader, [".eps"]))
            return self._finderCache[path]

    def find_spec(self, fullname, path, target=None):
        if path is None:
            path = sys.path
        for path_entry in path:
            finder = self._get_finder(path_entry)
            spec = finder.find_spec(fullname)
            if spec is None:
                continue
            return spec


sys.meta_path.append(EPSFinder())
