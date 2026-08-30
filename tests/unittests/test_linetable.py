import sys
import types
from bisect import bisect_right

from helper import *

from eudplib.bindings._rust import epscript
from eudplib.epscript.epsimp import _modify_code_linetable, lineno_regex

SOURCE = b"\n".join(
    [
        b"# (Line 10) def outer(x):",
        b"def outer(x):",
        b"# (Line 11)     def inner(y):",
        b"    def inner(y):",
        b"# (Line 12)         return 1 / y",
        b"        return 1 / y",
        b"# (Line 13)     return inner",
        b"    return inner",
        b"# (Line 14) triple = lambda v: v * 3",
        b"triple = lambda v: v * 3",
        b"# (Line 15) values = [triple(i) for i in range(3)]",
        b"values = [triple(i) for i in range(3)]",
        b"# (Line 16) def safe(y):",
        b"def safe(y):",
        b"# (Line 17)     try:",
        b"    try:",
        b"# (Line 18)         return outer(1)(y)",
        b"        return outer(1)(y)",
        b"# (Line 19)     except ZeroDivisionError:",
        b"    except ZeroDivisionError:",
        b"# (Line 20)         return -1",
        b"        return -1",
    ]
)

CODE_LINE = [0]
EP_LINENO_MAP = [0]
for lineno, line in enumerate(SOURCE.split(b"\n")):
    match = lineno_regex.match(line)
    if match:
        CODE_LINE.append(lineno + 1)
        EP_LINENO_MAP.append(max(0, int(match.group(1))))


def _expected_map(line):
    return EP_LINENO_MAP[bisect_right(CODE_LINE, line) - 1]


def _walk(codeobj):
    yield codeobj
    for const in codeobj.co_consts:
        if isinstance(const, types.CodeType):
            yield from _walk(const)


@TestInstance
def test_eps_linetable():
    if sys.version_info < (3, 11):
        return

    codeobj = compile(SOURCE, "test_linetable.py", "exec")
    line_map = epscript.LineMap(list(zip(CODE_LINE, EP_LINENO_MAP)))
    new_codeobj = _modify_code_linetable(codeobj, line_map)

    old_objects = list(_walk(codeobj))
    new_objects = list(_walk(new_codeobj))
    assert len(old_objects) == len(new_objects)

    for old, new in zip(old_objects, new_objects):
        assert new.co_name == old.co_name
        assert new.co_qualname == old.co_qualname
        assert new.co_code == old.co_code
        assert new.co_exceptiontable == old.co_exceptiontable
        assert new.co_firstlineno == _expected_map(old.co_firstlineno)

        old_positions = list(old.co_positions())
        new_positions = list(new.co_positions())
        assert len(new_positions) == len(new.co_code) // 2
        assert len(old_positions) == len(new_positions)
        for old_position, new_position in zip(old_positions, new_positions):
            assert (new_position[0] is None) == (old_position[0] is None)
            if old_position[0] is not None:
                assert new_position[0] == _expected_map(old_position[0])

        lines = list(new.co_lines())
        assert lines[0][0] == 0
        assert lines[-1][1] == len(new.co_code)
        for before, after in zip(lines, lines[1:]):
            assert before[1] == after[0]

    namespace = {}
    exec(new_codeobj, namespace)
    assert namespace["triple"](5) == 15
    assert namespace["values"] == [0, 3, 6]
    assert namespace["safe"](0) == -1

    try:
        namespace["outer"](1)(0)
    except ZeroDivisionError:
        tb = sys.exc_info()[2]
        while tb.tb_next is not None:
            tb = tb.tb_next
        assert tb.tb_lineno == 12
    else:
        raise AssertionError("ZeroDivisionError not raised")
