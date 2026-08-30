# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

class LineMap:
    def __new__(cls, points: list[tuple[int, int]]) -> LineMap: ...

def generate_linetable(
    line_map: LineMap, linetable: bytes, code: bytes, firstlineno: int
) -> tuple[int, bytes]: ...
