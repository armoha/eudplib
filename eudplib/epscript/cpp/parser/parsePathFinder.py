#!/usr/bin/python
# -*- coding: utf-8 -*-


# Print possible path to each states

import re

re_state = re.compile(r"^State (\d+):$")
re_shift = re.compile(r"^ +(\w+) shift  (\d+)$")

lines = open("epparser.out").readlines()

# Get graph
graph = {}
currentState = 0
for line in lines:
    r_st = re_state.match(line)
    if r_st:
        currentState = int(r_st.group(1))
        graph[currentState] = []
    else:
        r_sh = re_shift.match(line)
        if r_sh:
            token = r_sh.group(1)
            stateTo = int(r_sh.group(2))
            graph[currentState].append((token, stateTo))

# Find path
pathMap = {}
q = [("", 0)]

while q:
    prevPath, currentState = q.pop()
    for token, nextState in graph[currentState]:
        if nextState in pathMap:
            continue
        path = "%s %s" % (prevPath, token)
        pathMap[nextState] = path
        q.append((path, nextState))

keys = list(pathMap.keys())
keys.sort()
for k in keys:
    print("%5d :%s" % (k, pathMap[k]))
