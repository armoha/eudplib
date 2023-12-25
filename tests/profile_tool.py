import os
import sys
import time

_currentProfileTree = None


_last_time = time.process_time()


def _profiler(frame, event, arg):
    global _last_time
    global _currentProfileTree

    currentTime = time.process_time()
    elapsedTime = currentTime - _last_time

    if not _currentProfileTree:
        return

    if event == "call":
        try:
            newTree = _currentProfileTree[frame.f_code]
            newTree["_cumtime2"] = 0
            newTree["_calln"] += 1
        except KeyError:
            newTree = {
                "_code": frame.f_code,
                "_parent": _currentProfileTree,
                "_time": 0,
                "_calln": 1,
                "_cumtime": 0,
                "_cumtime2": 0,
            }
            _currentProfileTree[frame.f_code] = newTree
        _currentProfileTree["_time"] += elapsedTime
        _currentProfileTree["_cumtime"] += elapsedTime
        _currentProfileTree["_cumtime2"] += elapsedTime
        _currentProfileTree = newTree

        _last_time = time.process_time()

    elif event == "return":
        _currentProfileTree["_time"] += elapsedTime
        _currentProfileTree["_cumtime"] += elapsedTime

        parent = _currentProfileTree["_parent"]
        if parent:
            ct2 = _currentProfileTree["_cumtime2"] + elapsedTime
            parent["_cumtime"] += ct2
            parent["_cumtime2"] += ct2
            _currentProfileTree = parent
        else:
            _currentProfileTree = None

        _last_time = time.process_time()


def profile(f, ofname):
    global _currentProfileTree, _last_time
    _currentProfileTree = {
        "_code": None,
        "_parent": None,
        "_time": 0,
        "_cumtime": 0,
        "_cumtime2": 0,
    }
    rootTree = _currentProfileTree
    _last_time = time.process_time()
    sys.setprofile(_profiler)
    f()
    sys.setprofile(None)

    with open(ofname, "w") as output:
        _writeTree(output, rootTree, 0)


def _writeTree(output, tree, indent):
    header = "  " * indent
    for key in sorted(
        filter(lambda x: type(x) is not str, tree.keys()),
        key=lambda x: -tree[x]["_cumtime"],
    ):
        subtree = tree[key]
        code = subtree["_code"]
        if not code.co_name or code.co_name[0] == "_":
            continue

        sourcefname = os.path.split(code.co_filename)[-1]
        output.write(
            '%s"%s@%s:%d(%d / %f,%f)": {\n'
            % (
                header,
                code.co_name,
                sourcefname,
                code.co_firstlineno,
                subtree["_calln"],
                subtree["_cumtime"],
                subtree["_time"],
            )
        )
        _writeTree(output, subtree, indent + 1)
        output.write("%s},\n" % header)
