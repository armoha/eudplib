# Print possible path to each states

import re

re_state = re.compile(r"^State (\d+):$")
re_shift = re.compile(r"^ +(\w+) shift  (\d+)$")

with open("epparser.out") as file:
    lines = file.readlines()

# Get graph
graph: dict[int, list[tuple[str, int]]] = {}
_current_state: int = 0
for line in lines:
    r_st = re_state.match(line)
    if r_st:
        _current_state = int(r_st.group(1))
        graph[_current_state] = []
    else:
        r_sh = re_shift.match(line)
        if r_sh:
            token = r_sh.group(1)
            _state_to = int(r_sh.group(2))
            graph[_current_state].append((token, _state_to))

# Find path
_path_map = {}
q = [("", 0)]

while q:
    _prev_path, _current_state = q.pop()
    for token, _next_state in graph[_current_state]:
        if _next_state in _path_map:
            continue
        path = f"{_prev_path} {token}"
        _path_map[_next_state] = path
        q.append((path, _next_state))

keys = list(_path_map.keys())
keys.sort()
for k in keys:
    print("%5d :%s" % (k, _path_map[k]))
