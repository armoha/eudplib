#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from .eudarray import EUDArray


def EUDStack(basetype=None):
    class _EUDStack(c.EUDStruct):
        _fields_ = [("data", EUDArray), "pos"]

        def constructor(self, size):
            self.data = EUDArray(size)
            self.pos = 0

        def push(self, value):
            self.data[self.pos] = value
            self.pos += 1

        def pop(self):
            self.pos -= 1
            data = self.data[self.pos]
            if basetype:
                data = basetype.cast(data)
            return data

        def empty(self):
            return self.pos == 0

    return _EUDStack
