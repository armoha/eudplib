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
from bisect import bisect_right
from importlib.machinery import FileFinder, SourceFileLoader

from eudplib.localize import _
from eudplib.utils import EPError

from .epscompile import epsCompile
from .linetable_calculator import (
    PYCODE_ATTRIBUTES,
    gen_code_options,
    gen_new_opcode,
)

lineno_regex = re.compile(b" *# \\(Line (\\d+)\\) (.+)")
is_scdb_map = False


def IsSCDBMap():  # noqa: N802
    return is_scdb_map


def _modify_code_linetable(codeobj: types.CodeType, ep_lineno_map):
    # See: https://github.com/python/cpython/blob/main/Objects/locations.md
    # https://github.com/python/cpython/blob/c1652d6d6201e5407b94afc297115a584b5a0955/Python/assemble.c#L231-L242
    code_options = gen_code_options(codeobj)

    # For code objects
    new_co_consts = []
    for c in code_options["co_consts"]:
        if isinstance(c, types.CodeType):
            c = _modify_code_linetable(c, ep_lineno_map)
        new_co_consts.append(c)

    code_options["co_consts"] = new_co_consts

    return gen_new_opcode(
        codeobj, code_options, PYCODE_ATTRIBUTES, ep_lineno_map
    )


def _modify_code_lnotab(codeobj: types.CodeType, ep_lineno_map):
    # See: https://peps.python.org/pep-0626/#backwards-compatibility
    # https://github.com/python/cpython/blob/main/Objects/lnotab_notes.txt
    co_lnotab = codeobj.co_lnotab
    co_firstlineno = codeobj.co_firstlineno

    # Reconstruct co_lnotab
    new_lnotab = []
    current_line = co_firstlineno
    current_mapped_line = ep_lineno_map(current_line)
    for i in range(0, len(co_lnotab), 2):
        bytecode_len, line_advance = co_lnotab[i : i + 2]
        next_line = current_line + line_advance
        next_mapped_line = ep_lineno_map(next_line)
        new_line_advance = next_mapped_line - current_mapped_line
        while new_line_advance >= 0xFF:
            new_lnotab.append(bytes([0, 0xFF]))
            new_line_advance -= 0xFF
        new_lnotab.append(bytes([bytecode_len, new_line_advance]))
        current_line = next_line
        current_mapped_line = next_mapped_line

    # For code objects
    new_co_consts = []
    for c in codeobj.co_consts:
        if isinstance(c, types.CodeType):
            c = _modify_code_lnotab(c, ep_lineno_map)
        new_co_consts.append(c)

    # Python 3.7~3.10
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
        ep_lineno_map(co_firstlineno),  # codeobj.co_firstlineno,
        b"".join(new_lnotab),  # type: ignore
        codeobj.co_freevars,  # type: ignore
        codeobj.co_cellvars,  # type: ignore
    )

    return codeobj


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

        # Read lines from code data
        code_line = [0]
        ep_lineno_map = [0]
        data = data.replace(b"\r\n", b"\n")
        for lineno, line in enumerate(data.split(b"\n")):
            match = lineno_regex.match(line)
            if match:
                code_line.append(lineno + 1)
                ep_lineno_map.append(int(match.group(1)))

        # Reconstruct code data
        def line_mapper(line):
            if line is None:
                return None
            return ep_lineno_map[bisect_right(code_line, line) - 1]

        if "test_eps_epsfile" in path:
            print("code_line=", code_line)
            print("ep_lineno_map=", ep_lineno_map)

        if sys.version_info >= (3, 11):
            codeobj = _modify_code_linetable(codeobj, line_mapper)
        else:
            codeobj = _modify_code_lnotab(codeobj, line_mapper)
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
