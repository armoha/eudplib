import sys
import os
sys.path.insert(1, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))

import eudplib
import types
import re

module_to_doc = eudplib

exclude_types = [dict, str, types.ModuleType]
eudftypes = [eudplib.EUDFuncN]
allowed_type = eudftypes + [type, types.FunctionType]
exclude_names = ["__loader__", "__path__", "__spec__"]
section_header_charr = ["=", "-", "'", "~", "^"]


# Get list of already documented items
print("Getting list of currently documented structures")
rstinputs = open("api.rst", "r", encoding="utf-8").read().split("\n")
documented_functions = set()

func_regex = re.compile(r"-   \*\*(.+)?\*\*")

for line in rstinputs:
    func_match_result = func_regex.match(line)
    if func_match_result:
        funcname = func_match_result.groups(1)[0]
        print(funcname)
        if funcname in documented_functions:
            print("[Warning] Document duplication of function %s." % funcname)
        documented_functions.add(funcname)
        continue

print("Collecting list of documentation-needed structures")
doc_needed_functions = set()
fc_documented = {}


# Document module
for name, value in module_to_doc.__dict__.items():
    # Exclude list
    if name in exclude_names or type(value) in exclude_types:
        continue

    if not any(isinstance(value, t) for t in allowed_type):
        continue

    if value.__doc__ is None:
        print(" [Warning] undocumented value %s" % name)
        documented = False

    else:
        documented = True

    if isinstance(value, types.FunctionType) or isinstance(value, eudplib.EUDFuncN):
        doc_needed_functions.add(name)
        fc_documented[name] = documented

    elif type(value) is type:
        doc_needed_functions.add(name)
        fc_documented[name] = documented

print("\n==================================\n")


# Summary
"""
print('Current entries:')
print('  Functions:')
for k in doc_needed_functions:
    print('    - %s' % k)
print('  Classes:')
for k in doc_needed_classes:
    print('    - %s' % k)
print('==================================')
"""

# Diff
unused_functions = documented_functions.difference(doc_needed_functions)

if unused_functions:
    print("Entrys now unused:")
    if unused_functions:
        print("  Unused functions:")
        print(unused_functions)
        for k in sorted(list(unused_functions)):
            print("    - %s" % k)

    print("\n==================================\n")


# Diff2
used_functions = doc_needed_functions.difference(documented_functions)

if used_functions:
    print("New entries:")
    for k in sorted(list(used_functions)):
        print("    - %s %s" % (k, "(Undocumented)" if not fc_documented[k] else ""))

    print("\n==================================\n")

print("Diff done")
