#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Callable
from typing import ClassVar, TypeAlias, overload

from ...localize import _
from ...utils import EPError, ExprProxy, unProxy
from .. import variable as ev
from ..mapdata import GetPropertyIndex, UnitProperty
from .consttype import (
    Byte,
    ConstType,
    Dword,
    T,
    U,
    __Arg,
    __ExprProxy,
    _Arg,
    _Byte,
    _Dword,
    _ExprProxy,
)


class TrgAllyStatus(ConstType):
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {"Enemy": 0, "Ally": 1, "AlliedVictory": 2}


AllyStatus: TypeAlias = "TrgAllyStatus | Byte"
Enemy = TrgAllyStatus("Enemy")
Ally = TrgAllyStatus("Ally")
AlliedVictory = TrgAllyStatus("AlliedVictory")

AllyStatusDict: dict[ConstType, int] = {Enemy: 0, Ally: 1, AlliedVictory: 2}


class TrgComparison(ConstType):
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {"AtLeast": 0, "AtMost": 1, "Exactly": 10}


Comparison: TypeAlias = "TrgComparison | Byte"
AtLeast = TrgComparison("AtLeast")
AtMost = TrgComparison("AtMost")
Exactly = TrgComparison("Exactly")

ComparisonDict: dict[ConstType, int] = {AtLeast: 0, AtMost: 1, Exactly: 10}


class TrgCount(ConstType):
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {"All": 0}


Count: TypeAlias = "TrgCount | Byte"
All = TrgCount("All")


class TrgModifier(ConstType):
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {"SetTo": 7, "Add": 8, "Subtract": 9}


Modifier: TypeAlias = "TrgModifier | Byte"
SetTo = TrgModifier("SetTo")
Add = TrgModifier("Add")
Subtract = TrgModifier("Subtract")

ModifierDict: dict[ConstType, int] = {SetTo: 7, Add: 8, Subtract: 9}


class TrgOrder(ConstType):
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {"Move": 0, "Patrol": 1, "Attack": 2}


Order: TypeAlias = "TrgOrder | Byte"
Move = TrgOrder("Move")
Patrol = TrgOrder("Patrol")
Attack = TrgOrder("Attack")

OrderDict: dict[ConstType, int] = {Move: 0, Patrol: 1, Attack: 2}


class TrgPlayer(ConstType):
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {
        "P1": 0,
        "P2": 1,
        "P3": 2,
        "P4": 3,
        "P5": 4,
        "P6": 5,
        "P7": 6,
        "P8": 7,
        "P9": 8,
        "P10": 9,
        "P11": 10,
        "P12": 11,
        "Player1": 0,
        "Player2": 1,
        "Player3": 2,
        "Player4": 3,
        "Player5": 4,
        "Player6": 5,
        "Player7": 6,
        "Player8": 7,
        "Player9": 8,
        "Player10": 9,
        "Player11": 10,
        "Player12": 11,
        "CurrentPlayer": 13,
        "Foes": 14,
        "Allies": 15,
        "NeutralPlayers": 16,
        "AllPlayers": 17,
        "Force1": 18,
        "Force2": 19,
        "Force3": 20,
        "Force4": 21,
        "NonAlliedVictoryPlayers": 26,
    }


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
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {"Enable": 4, "Disable": 5, "Toggle": 6}


PropState: TypeAlias = "TrgPropState | Byte"
Enable = TrgPropState("Enable")
Disable = TrgPropState("Disable")
Toggle = TrgPropState("Toggle")

PropStateDict: dict[ConstType, int] = {Enable: 4, Disable: 5, Toggle: 6}


class TrgResource(ConstType):
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {"Ore": 0, "Gas": 1, "OreAndGas": 2}


Resource: TypeAlias = "TrgResource | Byte"
Ore = TrgResource("Ore")
Gas = TrgResource("Gas")
OreAndGas = TrgResource("OreAndGas")

ResourceDict: dict[ConstType, int] = {Ore: 0, Gas: 1, OreAndGas: 2}


class TrgScore(ConstType):
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {
        "Total": 0,
        "Units": 1,
        "Buildings": 2,
        "UnitsAndBuildings": 3,
        "Kills": 4,
        "Razings": 5,
        "KillsAndRazings": 6,
        "Custom": 7,
    }


class _KillsSpecialized(TrgScore):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._internalf: Callable

    # TODO: player: Player, comparison: Comparison, number: Dword, unit: Unit
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
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {
        "Set": 4,
        "Clear": 5,
        "Toggle": 6,
        "Random": 11,
    }


class TrgSwitchState(ConstType):
    __slots__ = ()
    _dict: ClassVar[dict[str, int]] = {"Set": 2, "Cleared": 3}


class TrgSwitchStateOrAction(TrgSwitchState, TrgSwitchAction):
    __slots__ = ()


SwitchState: TypeAlias = "TrgSwitchState | Byte"
SwitchAction: TypeAlias = "TrgSwitchAction | Byte"
Set = TrgSwitchStateOrAction("Set")
Clear = TrgSwitchAction("Clear")
Random = TrgSwitchAction("Random")
Cleared = TrgSwitchState("Cleared")

SwitchActionDict: dict[ConstType, int] = {
    Set: 4,
    Clear: 5,
    Toggle: 6,
    Random: 11,
}
SwitchStateDict: dict[ConstType, int] = {Set: 2, Cleared: 3}


@overload
def _EncodeConst(t: type[ConstType], s: ConstType) -> int:
    ...


@overload
def _EncodeConst(t: type[ConstType], s: T) -> T:
    ...


@overload
def _EncodeConst(t: type[ConstType], s: _ExprProxy) -> _Dword:
    ...


def _EncodeConst(t: type[ConstType], s: _Arg) -> _Dword:  # noqa: N802
    if isinstance(s, ConstType) and not isinstance(s, t):
        raise EPError(_('[Warning] "{}" is not a {}').format(s, t.__name__))
    return unProxy(s)  # type: ignore [return-value]


@overload
def EncodeAllyStatus(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeAllyStatus(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeAllyStatus(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeAllyStatus(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
    """Convert [Enemy, Ally, AlliedVictory] to number [0, 1, 2]."""
    try:
        return AllyStatusDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgAllyStatus, s)  # type: ignore[return-value]


@overload
def EncodeComparison(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeComparison(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeComparison(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeComparison(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
    """Convert [AtLeast, AtMost, Exactly] to number [0, 1, 10]."""
    try:
        return ComparisonDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgComparison, s)  # type: ignore[return-value]


@overload
def EncodeModifier(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeModifier(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeModifier(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeModifier(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
    """Convert [SetTo, Add, Subtract] to number [7, 8, 9]."""
    try:
        return ModifierDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgModifier, s)  # type: ignore[return-value]


@overload
def EncodeOrder(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeOrder(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeOrder(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeOrder(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
    """Convert [Move, Patrol, Attack] to number [0, 1, 2]."""
    try:
        return OrderDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgOrder, s)  # type: ignore[return-value]


@overload
def EncodePlayer(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodePlayer(s: T, issueError: bool = False) -> T:  # noqa: N803
    ...


@overload
def EncodePlayer(s: _ExprProxy, issueError: bool = False) -> _Dword:  # noqa: N803
    ...


def EncodePlayer(s: _Arg, issueError: bool = False) -> _Dword:  # noqa: N802, N803
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
    if type(s) is ev.EUDVariable:
        return s

    try:
        return PlayerDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgPlayer, s)


@overload
def EncodePropState(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodePropState(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodePropState(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodePropState(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
    """Convert [Enable, Disable, Toogle] to number [4, 5, 6]"""
    try:
        return PropStateDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgPropState, s)  # type: ignore[return-value]


@overload
def EncodeResource(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeResource(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeResource(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeResource(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
    """Convert [Ore, Gas, OreAndGas] to [0, 1, 2]"""
    try:
        return ResourceDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgResource, s)  # type: ignore[return-value]


@overload
def EncodeScore(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeScore(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeScore(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeScore(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
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
    try:
        return ScoreDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgScore, s)  # type: ignore[return-value]


@overload
def EncodeSwitchAction(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeSwitchAction(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeSwitchAction(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeSwitchAction(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
    """Convert [Set, Clear, Toogle, Random] to [4, 5, 6, 11]."""
    try:
        return SwitchActionDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgSwitchAction, s)  # type: ignore[return-value]


@overload
def EncodeSwitchState(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeSwitchState(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeSwitchState(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeSwitchState(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
    """Convert [Set, Cleared] to [2, 3]."""
    try:
        return SwitchStateDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgSwitchState, s)  # type: ignore[return-value]


@overload
def EncodeCount(s: ConstType, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeCount(s: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeCount(s: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeCount(s: __Arg, issueError: bool = False) -> _Byte:  # noqa: N802, N803
    """Convert [All, (other numbers)] to number [0, (as-is)]."""
    if s is All:
        return 0
    return _EncodeConst(TrgCount, s)  # type: ignore[return-value]


# ========================


def EncodeProperty(  # noqa: N802
    prop: UnitProperty | bytes | ExprProxy[UnitProperty | bytes],
    issueError: bool = False,  # noqa: N803
) -> int:
    prop = unProxy(prop)
    return GetPropertyIndex(prop)
