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
            with open(finalpath, encoding="utf-8") as file:
                code = file.read()
            totsize += len(code)
            linen = code.count("\n") + 1
            print(f"{finalpath:<40s} : {linen:4d}")
            totlinen += linen

print(f"Total lines: {totlinen}")
print(f"Total size: {totsize}")
