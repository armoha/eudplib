#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

beginning_str = """\
#!/usr/bin/python
# -*- coding: utf-8 -*-\
"""

print('Auto "license inserter')

for root, dirs, files in os.walk("../eudplib"):
    if "pybind11" in root:
        continue

    for f in files:
        if f[-3:] == ".py":
            finalpath = os.path.join(root, f)
            code = open(finalpath, "r", encoding="utf-8").read()

            if not code.startswith(beginning_str):
                print("%s" % finalpath)
                code = beginning_str + "\n" + code
                open(finalpath, "w", encoding="utf-8").write(code)

print("end")
