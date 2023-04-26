#!/usr/bin/python

import os

totlinen = 0
totsize = 0
totstrlist = []

for root, dirs, files in os.walk("../eudplib"):
    if "pybind11" in root:
        continue

    for f in files:
        if "cp949" in f:
            continue

        if f[-3:] == ".py":
            finalpath = os.path.join(root, f)
            code = open(finalpath, encoding="utf-8").read()
            totsize += len(code)
            linen = code.count("\n") + 1
            print("%-40s : %4d" % (finalpath, linen))
            totlinen += linen

print("Total lines: %d" % totlinen)
print("Total size: %d" % totsize)
