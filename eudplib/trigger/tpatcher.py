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
    _flush_filler,
)


def apply_patch_table(initepd, obj, patch_table: list[list[int | None]]) -> None:
    field_name = 0
    for i, patch_fields in enumerate(patch_table):
        for field_size in patch_fields:
            if isinstance(field_size, int):
                field = obj.fields[field_name]
                if c.IsEUDVariable(field):
                    memory_filler = {
                        -1: _filldw,
                        0: _fillloword,
                        # TODO: add _fillhiword? (ex. set action opcode & modifier)
                        2: _filllsbyte,
                        3: _filllobyte,
                        4: _fillhibyte,
                        5: _fillmsbyte,
                    }[field_size]
                    memory_filler(initepd + i, field)
                    obj.fields[field_name] = 0
            field_name += 1
    _flush_filler()


condpt: list[list[int | None]] = [
    [-1],
    [-1],
    [-1],
    [0, 4, 5],
    [2, 3, None, None],
]

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


def is_castable(cond) -> bool:
    # EUDArray, EUDVArray, EUDStruct, DBString
    return isinstance(cond, ExprProxy) and type(cond) is not ExprProxy


def patch_condition(cond: _Condition) -> Condition:
    castable = is_castable(cond)
    condition = unProxy(cond)
    if isinstance(condition, Forward):
        if not condition.IsSet():
            raise EPError(_("Forward not initialized"))
        condition = condition.expr
    if isinstance(condition, EUDLightBool):
        return c.MemoryX(condition.getValueAddr(), c.AtLeast, 1, condition._mask)
    if isinstance(condition, (EUDVariable, EUDLightVariable)):  # noqa: UP038
        return c.Memory(condition.getValueAddr(), c.AtLeast, 1)

    # translate boolean condition
    if isinstance(condition, (bool, int)):  # noqa: UP038
        return c.Always() if condition else c.Never()
    if isinstance(condition, Condition):
        apply_patch_table(EPD(condition), condition, condpt)
        return condition
    if castable and isinstance(condition, (ConstExpr, c.RlocInt_C)):  # noqa: UP038
        ep_warn(_("Condition is always True"))
        return c.Always() if condition != 0 else c.Never()
    raise EPError(_("Invalid input for condition: {}").format(cond))


def patch_action(act: Action | Forward | ExprProxy[Action | Forward]) -> Action:
    action = unProxy(act)
    if isinstance(action, Forward):
        if action._expr is None:
            raise EPError(_("Forward not initialized"))
        action = action._expr  # type: ignore[assignment]
    if not isinstance(action, Action):
        raise EPError(_("Action expected, found {}").format(act))
    apply_patch_table(EPD(action), action, actpt)
    return action


@overload
def is_const_cond(cond: Condition | ExprProxy[Condition]) -> bool:
    ...


@overload
def is_const_cond(cond: ConstCondition) -> Literal[True]:
    ...


def is_const_cond(cond) -> bool:
    castable = is_castable(cond)
    cond = unProxy(cond)
    if isinstance(cond, Forward):
        if cond._expr is None:
            return False
        cond = cond._expr
    if isinstance(cond, (bool, int, EUDVariable, EUDLightVariable, EUDLightBool)):  # noqa: UP038
        return True

    if isinstance(cond, Condition):
        field_name = 0
        for cond_fields in condpt:
            for field_size in cond_fields:
                if isinstance(field_size, int):
                    field = cond.fields[field_name]
                    if c.IsEUDVariable(field):
                        return False
                field_name += 1
        return True
    if castable and isinstance(cond, (ConstExpr, c.RlocInt_C)):  # noqa: UP038
        return True
    return False


@overload
def is_nagatable_cond(cond: Condition | ExprProxy[Condition]) -> bool:
    ...


@overload
def is_nagatable_cond(cond: ConstCondition) -> Literal[True]:
    ...


def is_nagatable_cond(cond) -> bool:
    castable = is_castable(cond)
    cond = unProxy(cond)
    if isinstance(cond, Forward):
        if cond._expr is None:
            return False
        cond = cond._expr
    if isinstance(cond, (bool, int, EUDVariable, EUDLightVariable, EUDLightBool)):  # noqa: UP038
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
            # AtMost and Exactly/AtLeast behaves differently in Bring/Command
            # (AtMost counts buildings on construction and does not count Egg)
            # So only exchanging (Exactly, 0) <-> (AtLeast, 1) is sound.
            #
            # See: https://cafe.naver.com/edac/book5095361/96809
            if condtype in bring_or_command:
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
    if castable and isinstance(cond, (ConstExpr, c.RlocInt_C)):  # noqa: UP038
        return True
    return False


def negate_cond(cond: _Condition) -> Condition:
    castable = is_castable(cond)
    condition = unProxy(cond)
    if isinstance(condition, Forward):
        if condition._expr is None:
            raise EPError(_("Forward not initialized"))
        condition = condition._expr
    if isinstance(condition, (EUDVariable, EUDLightVariable)):  # noqa: UP038
        return condition == 0
    if isinstance(condition, EUDLightBool):
        return condition.IsCleared()

    # translate boolean condition
    if isinstance(condition, (bool, int)):  # noqa: UP038
        return c.Never() if condition else c.Always()

    if isinstance(condition, Condition):
        condition.negate()
        return condition
    if castable and isinstance(condition, (ConstExpr, c.RlocInt_C)):  # noqa: UP038
        ep_warn(_("Condition is always False"))
        return c.Never() if condition == 0 else c.Always()
    raise EPError(_("Invalid input for condition: {}").format(cond))
