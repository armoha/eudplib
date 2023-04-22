#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, TypeAlias, overload

from .consttype import (
    ConstType,
    Dword,
    Byte,
    _Dword,
    _Byte,
    T,
    U,
    _ExprProxy,
    _Arg,
    __ExprProxy,
    __Arg,
)
from ...localize import _
from ...utils import ExprProxy, EPError, unProxy
from ..mapdata import GetPropertyIndex, UnitProperty

if TYPE_CHECKING:
    from ..allocator import ConstExpr
    from ..variable import EUDVariable


class TrgAllyStatus(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeAllyStatus(s)


AllyStatus: TypeAlias = "TrgAllyStatus | Byte"
Enemy = TrgAllyStatus("Enemy")
Ally = TrgAllyStatus("Ally")
AlliedVictory = TrgAllyStatus("AlliedVictory")

AllyStatusDict: dict[ConstType, int] = {Enemy: 0, Ally: 1, AlliedVictory: 2}


class TrgComparison(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeComparison(s)


Comparison: TypeAlias = "TrgComparison | Byte"
AtLeast = TrgComparison("AtLeast")
AtMost = TrgComparison("AtMost")
Exactly = TrgComparison("Exactly")

ComparisonDict: dict[ConstType, int] = {AtLeast: 0, AtMost: 1, Exactly: 10}


class TrgCount(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeCount(s)


Count: TypeAlias = "TrgCount | Byte"
All = TrgCount("All")


class TrgModifier(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeModifier(s)


Modifier: TypeAlias = "TrgModifier | Byte"
SetTo = TrgModifier("SetTo")
Add = TrgModifier("Add")
Subtract = TrgModifier("Subtract")

ModifierDict: dict[ConstType, int] = {SetTo: 7, Add: 8, Subtract: 9}


class TrgOrder(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeOrder(s)


Order: TypeAlias = "TrgOrder | Byte"
Move = TrgOrder("Move")
Patrol = TrgOrder("Patrol")
Attack = TrgOrder("Attack")

OrderDict: dict[ConstType, int] = {Move: 0, Patrol: 1, Attack: 2}


class TrgPlayer(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodePlayer(s)


Player: TypeAlias = "TrgPlayer | Dword"
P1 = TrgPlayer("P1")
P2 = TrgPlayer("P2")
P3 = TrgPlayer("P3")
P4 = TrgPlayer("P4")
P5 = TrgPlayer("P5")
P6 = TrgPlayer("P6")
P7 = TrgPlayer("P7")
P8 = TrgPlayer("P8")
P9 = TrgPlayer("P9")
P10 = TrgPlayer("P10")
P11 = TrgPlayer("P11")
P12 = TrgPlayer("P12")
Player1 = TrgPlayer("Player1")
Player2 = TrgPlayer("Player2")
Player3 = TrgPlayer("Player3")
Player4 = TrgPlayer("Player4")
Player5 = TrgPlayer("Player5")
Player6 = TrgPlayer("Player6")
Player7 = TrgPlayer("Player7")
Player8 = TrgPlayer("Player8")
Player9 = TrgPlayer("Player9")
Player10 = TrgPlayer("Player10")
Player11 = TrgPlayer("Player11")
Player12 = TrgPlayer("Player12")
CurrentPlayer = TrgPlayer("CurrentPlayer")
Foes = TrgPlayer("Foes")
Allies = TrgPlayer("Allies")
NeutralPlayers = TrgPlayer("NeutralPlayers")
AllPlayers = TrgPlayer("AllPlayers")
Force1 = TrgPlayer("Force1")
Force2 = TrgPlayer("Force2")
Force3 = TrgPlayer("Force3")
Force4 = TrgPlayer("Force4")
NonAlliedVictoryPlayers = TrgPlayer("NonAlliedVictoryPlayers")

PlayerDict: dict[ConstType, int] = {
    P1: 0,
    P2: 1,
    P3: 2,
    P4: 3,
    P5: 4,
    P6: 5,
    P7: 6,
    P8: 7,
    P9: 8,
    P10: 9,
    P11: 10,
    P12: 11,
    Player1: 0,
    Player2: 1,
    Player3: 2,
    Player4: 3,
    Player5: 4,
    Player6: 5,
    Player7: 6,
    Player8: 7,
    Player9: 8,
    Player10: 9,
    Player11: 10,
    Player12: 11,
    CurrentPlayer: 13,
    Foes: 14,
    Allies: 15,
    NeutralPlayers: 16,
    AllPlayers: 17,
    Force1: 18,
    Force2: 19,
    Force3: 20,
    Force4: 21,
    NonAlliedVictoryPlayers: 26,
}


class TrgProperty(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeProperty(s)


class TrgPropState(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodePropState(s)


PropState: TypeAlias = "TrgPropState | Byte"
Enable = TrgPropState("Enable")
Disable = TrgPropState("Disable")
Toggle = TrgPropState("Toggle")

PropStateDict: dict[ConstType, int] = {Enable: 4, Disable: 5, Toggle: 6}


class TrgResource(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeResource(s)


Resource: TypeAlias = "TrgResource | Byte"
Ore = TrgResource("Ore")
Gas = TrgResource("Gas")
OreAndGas = TrgResource("OreAndGas")

ResourceDict: dict[ConstType, int] = {Ore: 0, Gas: 1, OreAndGas: 2}


class TrgScore(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeScore(s)


class _KillsSpecialized(TrgScore):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._internalf: Callable

    # Player: Player, Comparison: Comparison, Number: Dword, Unit: Unit
    # ) -> Condition
    def __call__(self, a, b, c, d):
        return self._internalf(a, b, c, d)


Score: TypeAlias = "TrgScore | Byte"
Total = TrgScore("Total")
Units = TrgScore("Units")
Buildings = TrgScore("Buildings")
UnitsAndBuildings = TrgScore("UnitsAndBuildings")
# Name 'Kills' is used for both condition type and score type.
# To resolve conflict, we initialize Kills differently from others.
Kills = _KillsSpecialized("Kills")
Razings = TrgScore("Razings")
KillsAndRazings = TrgScore("KillsAndRazings")
Custom = TrgScore("Custom")

ScoreDict: dict[ConstType, int] = {
    Total: 0,
    Units: 1,
    Buildings: 2,
    UnitsAndBuildings: 3,
    Kills: 4,
    Razings: 5,
    KillsAndRazings: 6,
    Custom: 7,
}


class TrgSwitchAction(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeSwitchAction(s)


class TrgSwitchState(ConstType):
    @classmethod
    def cast(cls, s):
        return EncodeSwitchState(s)


class TrgSwitchStateOrAction(TrgSwitchState, TrgSwitchAction):
    pass


SwitchState: TypeAlias = "TrgSwitchState | Byte"
SwitchAction: TypeAlias = "TrgSwitchAction | Byte"
Set = TrgSwitchStateOrAction("Set")
Clear = TrgSwitchAction("Clear")
Random = TrgSwitchAction("Random")
Cleared = TrgSwitchState("Cleared")

SwitchActionDict: dict[ConstType, int] = {Set: 4, Clear: 5, Toggle: 6, Random: 11}
SwitchStateDict: dict[ConstType, int] = {Set: 2, Cleared: 3}


@overload
def _EncodeConst(t: str, d: Mapping[ConstType, int], s: ConstType) -> int:
    ...


@overload
def _EncodeConst(t: str, d: Mapping[ConstType, int], s: T) -> T:
    ...


@overload
def _EncodeConst(t: str, d: Mapping[ConstType, int], s: _ExprProxy) -> _Dword:
    ...


def _EncodeConst(t: str, d: Mapping[ConstType, int], s: _Arg) -> _Dword:
    u = unProxy(s)
    if isinstance(u, ConstType):
        if u in d:
            return d[u]
        raise EPError(_('[Warning] "{}" is not a {}').format(u, t))
    assert not isinstance(u, ExprProxy), "unreachable"
    return u


@overload
def EncodeAllyStatus(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodeAllyStatus(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeAllyStatus(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeAllyStatus(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [Enemy, Ally, AlliedVictory] to number [0, 1, 2]."""
    return _EncodeConst("AllyStatus", AllyStatusDict, s)  # type: ignore[return-value]


@overload
def EncodeComparison(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodeComparison(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeComparison(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeComparison(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [AtLeast, AtMost, Exactly] to number [0, 1, 10]."""
    return _EncodeConst("Comparison", ComparisonDict, s)  # type: ignore[return-value]


@overload
def EncodeModifier(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodeModifier(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeModifier(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeModifier(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [SetTo, Add, Subtract] to number [7, 8, 9]."""
    return _EncodeConst("Modifier", ModifierDict, s)  # type: ignore[return-value]


@overload
def EncodeOrder(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodeOrder(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeOrder(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeOrder(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [Move, Patrol, Attack] to number [0, 1, 2]."""
    return _EncodeConst("Order", OrderDict, s)  # type: ignore[return-value]


@overload
def EncodePlayer(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodePlayer(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodePlayer(s: _ExprProxy, issueError: bool = False) -> _Dword:
    ...


def EncodePlayer(s: _Arg, issueError: bool = False) -> _Dword:
    """Convert player identifier to corresponding number.

    ======================= ========
        Identifier           Number
    ======================= ========
    P1                         0
    P2                         1
    P3                         2
    P4                         3
    P5                         4
    P6                         5
    P7                         6
    P8                         7
    P9                         8
    P10                        9
    P11                        10
    P12                        11
    Player1                    0
    Player2                    1
    Player3                    2
    Player4                    3
    Player5                    4
    Player6                    5
    Player7                    6
    Player8                    7
    Player9                    8
    Player10                   9
    Player11                   10
    Player12                   11
    CurrentPlayer              13
    Foes                       14
    Allies                     15
    NeutralPlayers             16
    AllPlayers                 17
    Force1                     18
    Force2                     19
    Force3                     20
    Force4                     21
    NonAlliedVictoryPlayers    26
    ======================= ========

    """
    return _EncodeConst("Player", PlayerDict, s)


@overload
def EncodePropState(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodePropState(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodePropState(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodePropState(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [Enable, Disable, Toogle] to number [4, 5, 6]"""
    return _EncodeConst("PropState", PropStateDict, s)  # type: ignore[return-value]


@overload
def EncodeResource(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodeResource(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeResource(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeResource(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [Ore, Gas, OreAndGas] to [0, 1, 2]"""
    return _EncodeConst("Resource", ResourceDict, s)  # type: ignore[return-value]


@overload
def EncodeScore(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodeScore(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeScore(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeScore(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert score type identifier to number.

    ================= ========
        _Score type     Number
    ================= ========
    Total                0
    Units                1
    Buildings            2
    UnitsAndBuildings    3
    Kills                4
    Razings              5
    KillsAndRazings      6
    Custom               7
    ================= ========

    """
    return _EncodeConst("Score", ScoreDict, s)  # type: ignore[return-value]


@overload
def EncodeSwitchAction(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodeSwitchAction(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeSwitchAction(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeSwitchAction(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [Set, Clear, Toogle, Random] to [4, 5, 6, 11]."""
    return _EncodeConst("SwitchAction", SwitchActionDict, s)  # type: ignore[return-value]


@overload
def EncodeSwitchState(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodeSwitchState(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeSwitchState(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeSwitchState(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [Set, Cleared] to [2, 3]."""
    return _EncodeConst("_SwitchState", SwitchStateDict, s)  # type: ignore[return-value]


@overload
def EncodeCount(s: ConstType, issueError: bool = False) -> int:
    ...


@overload
def EncodeCount(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeCount(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeCount(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [All, (other numbers)] to number [0, (as-is)]."""
    t = unProxy(s)
    if t is All:
        return 0
    if isinstance(t, ConstType):
        raise EPError(_('[Warning] "{}" is not a {}').format(s, "count"))
    assert not isinstance(t, ExprProxy), "unreachable"
    return t


# ========================


def EncodeProperty(
    prop: UnitProperty | bytes | ExprProxy[UnitProperty | bytes], issueError: bool = False
) -> int:
    prop = unProxy(prop)
    return GetPropertyIndex(prop)
