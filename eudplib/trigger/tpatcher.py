#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from .. import core as c
from .. import utils as ut
from .filler import _filldw, _fillloword, _filllsbyte, _filllobyte, _fillhibyte, _fillmsbyte


def ApplyPatchTable(initepd, obj, patchTable):
    def fieldSelector(fieldName):
        if type(fieldName) is int:
            return obj.fields[fieldName]
        else:
            return 0

    fieldName = 0
    for i, patchEntry in enumerate(patchTable):
        patchFields = patchEntry
        for fieldSize in patchFields:
            if type(fieldSize) is int:
                memoryFiller = {
                    -1: _filldw, 0: _fillloword,
                    2: _filllsbyte, 3: _filllobyte,
                    4: _fillhibyte, 5: _fillmsbyte
                }[fieldSize]
                field = fieldSelector(fieldName)
                if ut.isUnproxyInstance(field, c.EUDVariable):
                    memoryFiller(initepd + i, field)
                    obj.fields[fieldName] = 0
            fieldName += 1


condpt = [[-1], [-1], [-1], [0, 4, 5], [2, 3, None, None]]

actpt = [[-1], [-1], [-1], [-1], [-1], [-1], [0, 4, 5], [2, None, None, None]]


def PatchCondition(cond):
    if ut.isUnproxyInstance(cond, c.EUDVariable):
        return cond >= 1

    # translate boolean condition
    elif isinstance(cond, bool):
        if cond:
            return c.Always()
        else:
            return c.Never()

    else:
        try:
            ApplyPatchTable(ut.EPD(cond), cond, condpt)
            return cond
        except AttributeError as e:
            if c.IsConstExpr(cond):
                return cond != 0
            raise


def PatchAction(act):
    ApplyPatchTable(ut.EPD(act), act, actpt)
    return act
