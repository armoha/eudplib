#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

def stack_objects(dwoccupmap_list: list[list[int]]) -> list[int]: ...

class ConstExpr:
    def __init__(
        self, baseobj: "ConstExpr | None", offset: int, rlocmode: int
    ) -> None: ...
