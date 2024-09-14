# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


class Payload:
    def __init__(self, data: bytes, prttable: list[int], orttable: list[int]) -> None:
        self.data = data
        self.prttable = prttable
        self.orttable = orttable
