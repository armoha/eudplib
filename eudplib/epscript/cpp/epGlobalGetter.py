#!/usr/bin/python
# -*- coding: utf-8 -*-


import eudplib
import types
import re

# mode = 1  # Get functions
# mode = 2  # Get globals
mode = 3  # Everything

module_to_doc = eudplib

exclude_types = [dict, str, types.ModuleType]
eudftypes = [eudplib.core.eudfunc.eudfuncn.EUDFuncN]
if mode == 1:
    allowed_type = eudftypes + [
        type,
        types.FunctionType,
        eudplib.core.rawtrigger.constenc._KillsSpecialized,
    ]
elif mode == 2:
    allowed_type = [
        int,
        eudplib.core.rawtrigger.constenc._Unique,
        eudplib.core.rawtrigger.constenc._KillsSpecialized,
    ]
else:
    allowed_type = eudftypes + [
        int,
        eudplib.core.rawtrigger.constenc._Unique,
        type,
        types.FunctionType,
        eudplib.core.rawtrigger.constenc._KillsSpecialized,
    ]
exclude_names = ["__loader__", "__path__", "__spec__"]
section_header_charr = ["=", "-", "'", "~", "^"]


print("Collecting list of documentation-needed structures")
doc_needed_functions = set()
doc_needed_classes = set()
fc_documented = {}


# Document module
nlist = []
for name, value in module_to_doc.__dict__.items():
    # Exclude list
    if name in exclude_names or type(value) in exclude_types:
        continue

    # Undocumented -> ignore
    if not any(isinstance(value, t) for t in allowed_type):
        continue

    else:
        documented = True

    nlist.append(name)

if mode != 2:
    nlist.extend(["beforeTriggerExec", "afterTriggerExec", "onPluginStart", "settings"])
print("\n==================================\n")
nlist.sort()
nlist = ['"%s", ' % name for name in nlist]
col = 4
s = []


def flush():
    global col
    print("    " + "".join(s))
    col = 4
    s.clear()


for n in nlist:
    if col + len(n) >= 80:
        flush()
    s.append(n)
    col += len(n)
flush()
