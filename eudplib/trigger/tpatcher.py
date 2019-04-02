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
from .filler import _filldw, _fillwbb, _fillbbbb


def HasEUDVariable(l):
    for i in l:
        i = ut.unProxy(i)
        if isinstance(i, c.EUDVariable):
            return True
    return False


def ApplyPatchTable(initepd, obj, patchTable):
    def fieldSelector(fieldName):
        if type(fieldName) is int:
            return obj.fields[fieldName]
        else:
            return 0

    for i, patchEntry in enumerate(patchTable):
        patchFields = patchEntry
        memoryFiller = {1: _filldw, 3: _fillwbb, 4: _fillbbbb}[len(patchFields)]

        fieldList = list(map(fieldSelector, patchFields))
        if HasEUDVariable(fieldList):
            memoryFiller(initepd + i, *fieldList)
            for fieldName in patchFields:
                if type(fieldName) is int:
                    obj.fields[fieldName] = 0


condpt = [[0], [1], [2], [3, 4, 5], [6, 7, None, None]]

actpt = [[0], [1], [2], [3], [4], [5], [6, 7, 8], [9, None, None, None]]


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
