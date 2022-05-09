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
from .filler import (
    _filldw,
    _fillloword,
    _filllsbyte,
    _filllobyte,
    _fillhibyte,
    _fillmsbyte,
)


def ApplyPatchTable(initepd, obj, patchTable):
    fieldName = 0
    for i, patchEntry in enumerate(patchTable):
        patchFields = patchEntry
        for fieldSize in patchFields:
            if type(fieldSize) is int:
                memoryFiller = {
                    -1: _filldw,
                    0: _fillloword,
                    2: _filllsbyte,
                    3: _filllobyte,
                    4: _fillhibyte,
                    5: _fillmsbyte,
                }[fieldSize]
                field = obj.fields[fieldName]
                if c.IsEUDVariable(field):
                    memoryFiller(initepd + i, field)
                    obj.fields[fieldName] = 0
            fieldName += 1


condpt = [[-1], [-1], [-1], [0, 4, 5], [2, 3, None, None]]

actpt = [[-1], [-1], [-1], [-1], [-1], [-1], [0, 4, 5], [2, None, None, None]]


def PatchCondition(cond):
    if hasattr(cond, "getValueAddr"):
        try:  # EUDLightBool, EUDEntry
            return c.MemoryX(cond.getValueAddr(), c.AtLeast, 1, cond._mask)
        except AttributeError:  # EUD(Light)Variable, Db
            return c.Memory(cond.getValueAddr(), c.AtLeast, 1)

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
        except AttributeError:
            if c.IsConstExpr(cond):
                return cond != 0
            raise


def PatchAction(act):
    ApplyPatchTable(ut.EPD(act), act, actpt)
    return act


def IsConditionConst(cond):
    if c.IsEUDVariable(cond):
        return True
    elif ut.isUnproxyInstance(cond, c.EUDLightVariable):
        return True
    elif ut.isUnproxyInstance(cond, c.EUDLightBool):
        return True
    elif isinstance(cond, bool):
        return True
    else:
        try:
            fieldName = 0
            for condFields in condpt:
                for fieldSize in condFields:
                    if type(fieldSize) is int:
                        field = cond.fields[fieldName]
                        if c.IsEUDVariable(field):
                            return False
                    fieldName += 1
            return True
        except AttributeError:
            if c.IsConstExpr(cond):
                return True
            return False


def IsConditionNegatable(cond):
    if c.IsEUDVariable(cond):
        return True
    elif ut.isUnproxyInstance(cond, c.EUDLightVariable):
        return True
    elif ut.isUnproxyInstance(cond, c.EUDLightBool):
        return True
    elif isinstance(cond, bool):
        return True
    else:
        try:
            condtype = cond.fields[5]
            comparison_set = (1, 2, 3, 4, 5, 12, 14, 15, 21)
            always_or_never = (0, 22, 13, 23)
            if condtype in always_or_never:
                return True
            if condtype == 11:  # Switch
                return True
            if condtype in comparison_set:
                bring_or_command = (2, 3)
                comparison = cond.fields[4]
                amount = cond.fields[2] & 0xFFFFFFFF
                if comparison == 10 and amount == 0:
                    return True
                if comparison == 0 and amount <= 1:
                    return True
                if condtype in bring_or_command:
                    # AtMost and Exactly/AtLeast behaves differently in Bring or Command.
                    # (ex. AtMost counts buildings on construction and does not count Egg/Cocoon)
                    # So only exchanging (Exactly, 0) <-> (AtLeast, 1) is sound.
                    #
                    # See: https://cafe.naver.com/edac/book5095361/96809
                    return False
                if comparison in (0, 1):
                    return True
                elif comparison != 10:
                    return False
                elif condtype == 15 and cond.fields[8] == ut.b2i2(ut.u2b("SC")):
                    mask = cond.fields[0] & 0xFFFFFFFF
                    if amount & (~mask):  # never
                        return True
                    if amount == mask:
                        return True
                    return False
                elif amount == 0xFFFFFFFF:
                    return True
            return False
        except AttributeError:
            if c.IsConstExpr(cond):
                return True
            return False


def NegateCondition(cond):
    if c.IsEUDVariable(cond):
        return cond == 0
    elif ut.isUnproxyInstance(cond, c.EUDLightVariable):
        return cond == 0
    elif ut.isUnproxyInstance(cond, c.EUDLightBool):
        return cond.IsCleared()

    # translate boolean condition
    elif isinstance(cond, bool):
        if cond:
            return c.Never()
        else:
            return c.Always()

    else:
        try:
            cond.Negate()
            return cond
        except (AttributeError, ut.EPError):
            if c.IsConstExpr(cond):
                return cond == 0
            raise
