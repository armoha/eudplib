#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Literal, overload

from eudplib.localize import _

from .. import core as c
from ..core import (
    Action,
    Condition,
    ConstExpr,
    EUDLightBool,
    EUDLightVariable,
    EUDVariable,
    Forward,
)
from ..utils import EPD, EPError, ExprProxy, ep_warn, unProxy
from .filler import (
    _filldw,
    _fillhibyte,
    _filllobyte,
    _fillloword,
    _filllsbyte,
    _fillmsbyte,
)


def ApplyPatchTable(initepd, obj, patchTable: list[list[int | None]]) -> None:
    fieldName = 0
    for i, patchEntry in enumerate(patchTable):
        patchFields = patchEntry
        for fieldSize in patchFields:
            if isinstance(fieldSize, int):
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


condpt: list[list[int | None]] = [[-1], [-1], [-1], [0, 4, 5], [2, 3, None, None]]

actpt: list[list[int | None]] = [
    [-1],
    [-1],
    [-1],
    [-1],
    [-1],
    [-1],
    [0, 4, 5],
    [2, None, None, None],
]

ConstCondition = (
    bool
    | int
    | EUDVariable
    | EUDLightVariable
    | EUDLightBool
    | ExprProxy[bool | int | EUDVariable | EUDLightVariable | EUDLightBool]
)
_Condition = ConstExpr | ConstCondition | ExprProxy[ConstExpr]


def isCastable(cond) -> bool:
    # EUDArray, EUDVArray, EUDStruct, DBString
    return isinstance(cond, ExprProxy) and type(cond) is not ExprProxy


def PatchCondition(cond: _Condition) -> Condition:
    is_castable = isCastable(cond)
    condition = unProxy(cond)
    if isinstance(condition, Forward):
        if condition._expr is None:
            raise EPError(_("Forward not initialized"))
        condition = condition._expr
    if isinstance(condition, EUDLightBool):
        return c.MemoryX(condition.getValueAddr(), c.AtLeast, 1, condition._mask)
    if isinstance(condition, (EUDVariable, EUDLightVariable)):
        return c.Memory(condition.getValueAddr(), c.AtLeast, 1)

    # translate boolean condition
    if isinstance(condition, (bool, int)):
        return c.Always() if condition else c.Never()
    if isinstance(condition, Condition):
        ApplyPatchTable(EPD(condition), condition, condpt)
        return condition
    if is_castable and isinstance(condition, (ConstExpr, c.RlocInt_C)):
        ep_warn(_("Condition is always True"))
        return c.Always() if condition != 0 else c.Never()
    raise EPError(_("Invalid input for condition: {}").format(cond))


def PatchAction(act: Action | Forward | ExprProxy[Action | Forward]) -> Action:
    action = unProxy(act)
    if isinstance(action, Forward):
        if action._expr is None:
            raise EPError(_("Forward not initialized"))
        action = action._expr  # type: ignore[assignment]
    if not isinstance(action, Action):
        raise EPError(_("Action expected, found {}").format(act))
    ApplyPatchTable(EPD(action), action, actpt)
    return action


@overload
def IsConditionConst(cond: Condition | ExprProxy[Condition]) -> bool:
    ...


@overload
def IsConditionConst(cond: ConstCondition) -> Literal[True]:
    ...


def IsConditionConst(cond) -> bool:
    is_castable = isCastable(cond)
    cond = unProxy(cond)
    if isinstance(cond, Forward):
        if cond._expr is None:
            return False
        cond = cond._expr
    if isinstance(cond, (bool, int, EUDVariable, EUDLightVariable, EUDLightBool)):
        return True

    if isinstance(cond, Condition):
        fieldName = 0
        for condFields in condpt:
            for fieldSize in condFields:
                if isinstance(fieldSize, int):
                    field = cond.fields[fieldName]
                    if c.IsEUDVariable(field):
                        return False
                fieldName += 1
        return True
    if is_castable and isinstance(cond, (ConstExpr, c.RlocInt_C)):
        return True
    return False


@overload
def IsConditionNegatable(cond: Condition | ExprProxy[Condition]) -> bool:
    ...


@overload
def IsConditionNegatable(cond: ConstCondition) -> Literal[True]:
    ...


def IsConditionNegatable(cond) -> bool:
    is_castable = isCastable(cond)
    cond = unProxy(cond)
    if isinstance(cond, Forward):
        if cond._expr is None:
            return False
        cond = cond._expr
    if isinstance(cond, (bool, int, EUDVariable, EUDLightVariable, EUDLightBool)):
        return True

    if isinstance(cond, Condition):
        condtype = cond.fields[5]
        if not isinstance(condtype, int):
            return False
        comparison_set = (1, 2, 3, 4, 5, 12, 14, 15, 21)
        always_or_never = (0, 22, 13, 23)
        if condtype in always_or_never:
            return True
        comparison = cond.fields[4]
        if not isinstance(comparison, int):
            return False
        if condtype == 11 and comparison in (2, 3):  # Switch
            return True
        amount = cond.fields[2]
        if condtype in comparison_set and isinstance(amount, int):
            bring_or_command = (2, 3)
            amount &= 0xFFFFFFFF
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
            elif (
                condtype == 15
                and isinstance(cond.fields[8], int)
                and cond.fields[8] == 0x4353
            ):
                mask = cond.fields[0]
                if not isinstance(mask, int):
                    return False
                mask &= 0xFFFFFFFF
                if amount & (~mask):  # never
                    return True
                if amount == mask:
                    return True
                return False
            elif amount == 0xFFFFFFFF:
                return True
        return False
    if is_castable and isinstance(cond, (ConstExpr, c.RlocInt_C)):
        return True
    return False


def NegateCondition(cond: _Condition) -> Condition:
    is_castable = isCastable(cond)
    condition = unProxy(cond)
    if isinstance(condition, Forward):
        if condition._expr is None:
            raise EPError(_("Forward not initialized"))
        condition = condition._expr
    if isinstance(condition, (EUDVariable, EUDLightVariable)):
        return condition == 0
    if isinstance(condition, EUDLightBool):
        return condition.IsCleared()

    # translate boolean condition
    if isinstance(condition, (bool, int)):
        return c.Never() if condition else c.Always()

    if isinstance(condition, Condition):
        condition.Negate()
        return condition
    if is_castable and isinstance(condition, (ConstExpr, c.RlocInt_C)):
        ep_warn(_("Condition is always False"))
        return c.Never() if condition == 0 else c.Always()
    raise EPError(_("Invalid input for condition: {}").format(cond))
