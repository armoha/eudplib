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

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, TypeAlias, TypeVar, overload

from ... import utils as ut
from ...localize import _
from ...utils import ExprProxy
from ..mapdata import GetPropertyIndex, UnitProperty

if TYPE_CHECKING:
    from ..allocator import ConstExpr
    from ..variable import EUDVariable

Dword: TypeAlias = "int | EUDVariable | ConstExpr | ExprProxy[int] | ExprProxy[EUDVariable] | ExprProxy[ConstExpr]"
Word: TypeAlias = "int | EUDVariable | ExprProxy[int] | ExprProxy[EUDVariable]"
Byte: TypeAlias = "int | EUDVariable | ExprProxy[int] | ExprProxy[EUDVariable]"


class _Unique:
    def __init__(self, name: str) -> None:
        self._name: str = name

    def __repr__(self) -> str:
        return self._name

    def __str__(self) -> str:
        return repr(self)


class _Player(_Unique):
    pass


Player: TypeAlias = "_Player | Dword"
P1 = _Player("P1")
P2 = _Player("P2")
P3 = _Player("P3")
P4 = _Player("P4")
P5 = _Player("P5")
P6 = _Player("P6")
P7 = _Player("P7")
P8 = _Player("P8")
P9 = _Player("P9")
P10 = _Player("P10")
P11 = _Player("P11")
P12 = _Player("P12")
Player1 = _Player("Player1")
Player2 = _Player("Player2")
Player3 = _Player("Player3")
Player4 = _Player("Player4")
Player5 = _Player("Player5")
Player6 = _Player("Player6")
Player7 = _Player("Player7")
Player8 = _Player("Player8")
Player9 = _Player("Player9")
Player10 = _Player("Player10")
Player11 = _Player("Player11")
Player12 = _Player("Player12")
CurrentPlayer = _Player("CurrentPlayer")
Foes = _Player("Foes")
Allies = _Player("Allies")
NeutralPlayers = _Player("NeutralPlayers")
AllPlayers = _Player("AllPlayers")
Force1 = _Player("Force1")
Force2 = _Player("Force2")
Force3 = _Player("Force3")
Force4 = _Player("Force4")
NonAlliedVictoryPlayers = _Player("NonAlliedVictoryPlayers")


class _Score(_Unique):
    pass


class _KillsSpecialized(_Score):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._internalf: Callable

    def __call__(self, a, b, c, d):
        return self._internalf(a, b, c, d)


Score: TypeAlias = "_Score | Byte"
Total = _Score("Total")
Units = _Score("Units")
Buildings = _Score("Buildings")
UnitsAndBuildings = _Score("UnitsAndBuildings")
# Name 'Kills' is used for both condition type and score type.
# To resolve conflict, we initialize Kills differently from others.
Kills = _KillsSpecialized("Kills")
Razings = _Score("Razings")
KillsAndRazings = _Score("KillsAndRazings")
Custom = _Score("Custom")


class _Resource(_Unique):
    pass


Resource: TypeAlias = "_Resource | Byte"
Ore = _Resource("Ore")
Gas = _Resource("Gas")
OreAndGas = _Resource("OreAndGas")


class _AllyStatus(_Unique):
    pass


AllyStatus: TypeAlias = "_AllyStatus | Byte"
Enemy = _AllyStatus("Enemy")
Ally = _AllyStatus("Ally")
AlliedVictory = _AllyStatus("AlliedVictory")


class _Comparison(_Unique):
    pass


Comparison: TypeAlias = "_Comparison | Byte"
AtLeast = _Comparison("AtLeast")
AtMost = _Comparison("AtMost")
Exactly = _Comparison("Exactly")


class _Modifier(_Unique):
    pass


Modifier: TypeAlias = "_Modifier | Byte"
SetTo = _Modifier("SetTo")
Add = _Modifier("Add")
Subtract = _Modifier("Subtract")


class _SwitchState(_Unique):
    pass


class _SwitchAction(_Unique):
    pass


class _SwitchStateOrAction(_SwitchState, _SwitchAction):
    pass


SwitchState: TypeAlias = "_SwitchState | Byte"
SwitchAction: TypeAlias = "_SwitchAction | Byte"
Set = _SwitchStateOrAction("Set")
Clear = _SwitchAction("Clear")
Random = _SwitchAction("Random")
Cleared = _SwitchState("Cleared")


class _PropState(_Unique):
    pass


PropState: TypeAlias = "_PropState | Byte"
Enable = _PropState("Enable")
Disable = _PropState("Disable")
Toggle = _PropState("Toggle")


class _Count(_Unique):
    pass


Count: TypeAlias = "_Count | Byte"
All = _Count("All")


class _Order(_Unique):
    pass


Order: TypeAlias = "_Order | Byte"
Move = _Order("Move")
Patrol = _Order("Patrol")
Attack = _Order("Attack")

AllyStatusDict: dict[_Unique, int] = {Enemy: 0, Ally: 1, AlliedVictory: 2}

ComparisonDict: dict[_Unique, int] = {AtLeast: 0, AtMost: 1, Exactly: 10}

ModifierDict: dict[_Unique, int] = {SetTo: 7, Add: 8, Subtract: 9}

OrderDict: dict[_Unique, int] = {Move: 0, Patrol: 1, Attack: 2}

PlayerDict: dict[_Unique, int] = {
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

PropStateDict: dict[_Unique, int] = {Enable: 4, Disable: 5, Toggle: 6}

ResourceDict: dict[_Unique, int] = {Ore: 0, Gas: 1, OreAndGas: 2}

ScoreDict: dict[_Unique, int] = {
    Total: 0,
    Units: 1,
    Buildings: 2,
    UnitsAndBuildings: 3,
    Kills: 4,
    Razings: 5,
    KillsAndRazings: 6,
    Custom: 7,
}

SwitchActionDict: dict[_Unique, int] = {Set: 4, Clear: 5, Toggle: 6, Random: 11}

SwitchStateDict: dict[_Unique, int] = {Set: 2, Cleared: 3}

# return types
_Dword: TypeAlias = "int | EUDVariable | ConstExpr"
_Word: TypeAlias = "int | EUDVariable"
_Byte: TypeAlias = "int | EUDVariable"
# argument types
T = TypeVar("T", int, "EUDVariable", "ConstExpr")
U = TypeVar("U", int, "EUDVariable")
_ExprProxy: TypeAlias = "ExprProxy[_Unique | int | EUDVariable | ConstExpr | ExprProxy]"
_Arg: TypeAlias = "_Unique | int | EUDVariable | ConstExpr | ExprProxy[_Unique | int | EUDVariable | ConstExpr | ExprProxy]"
__ExprProxy: TypeAlias = "ExprProxy[_Unique | int | EUDVariable | ExprProxy]"
__Arg: TypeAlias = (
    "_Unique | int | EUDVariable | ExprProxy[_Unique | int | EUDVariable | ExprProxy]"
)


@overload
def _EncodeConst(t: str, d: Mapping[_Unique, int], s: _Unique) -> int:
    ...


@overload
def _EncodeConst(t: str, d: Mapping[_Unique, int], s: T) -> T:
    ...


@overload
def _EncodeConst(t: str, d: Mapping[_Unique, int], s: _ExprProxy) -> _Dword:
    ...


def _EncodeConst(t: str, d: Mapping[_Unique, int], s: _Arg) -> _Dword:
    u = ut.unProxy(s)
    if isinstance(u, _Unique):
        if u in d:
            return d[u]
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(u, t))
    assert not isinstance(u, ExprProxy), "unreachable"
    return u


@overload
def EncodeAllyStatus(s: _Unique, issueError: bool = False) -> int:
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
def EncodeComparison(s: _Unique, issueError: bool = False) -> int:
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
def EncodeModifier(s: _Unique, issueError: bool = False) -> int:
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
def EncodeOrder(s: _Unique, issueError: bool = False) -> int:
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
def EncodePlayer(s: _Unique, issueError: bool = False) -> int:
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
def EncodePropState(s: _Unique, issueError: bool = False) -> int:
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
def EncodeResource(s: _Unique, issueError: bool = False) -> int:
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
def EncodeScore(s: _Unique, issueError: bool = False) -> int:
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
def EncodeSwitchAction(s: _Unique, issueError: bool = False) -> int:
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
def EncodeSwitchState(s: _Unique, issueError: bool = False) -> int:
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
def EncodeCount(s: _Unique, issueError: bool = False) -> int:
    ...


@overload
def EncodeCount(s: U, issueError: bool = False) -> U:
    ...


@overload
def EncodeCount(s: __ExprProxy, issueError: bool = False) -> _Byte:
    ...


def EncodeCount(s: __Arg, issueError: bool = False) -> _Byte:
    """Convert [All, (other numbers)] to number [0, (as-is)]."""
    t = ut.unProxy(s)
    if t is All:
        return 0
    if isinstance(t, _Unique):
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, "count"))
    assert not isinstance(t, ExprProxy), "unreachable"
    return t


# ========================


def EncodeProperty(
    prop: UnitProperty | bytes | ExprProxy[UnitProperty | bytes], issueError: bool = False
) -> int:
    prop = ut.unProxy(prop)
    return GetPropertyIndex(prop)
