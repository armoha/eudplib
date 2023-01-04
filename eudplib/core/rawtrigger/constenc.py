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

from collections.abc import Callable
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


class _PlayerGroup(_Player):
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
Foes = _PlayerGroup("Foes")
Allies = _PlayerGroup("Allies")
NeutralPlayers = _PlayerGroup("NeutralPlayers")
AllPlayers = _PlayerGroup("AllPlayers")
Force1 = _PlayerGroup("Force1")
Force2 = _PlayerGroup("Force2")
Force3 = _PlayerGroup("Force3")
Force4 = _PlayerGroup("Force4")
NonAlliedVictoryPlayers = _PlayerGroup("NonAlliedVictoryPlayers")


class _Score(_Unique):
    pass


class _KillsSpecialized(_Score):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._internalf: Callable

    def __call__(self, a, b, c, d):
        return self._internalf(a, b, c, d)


Score: TypeAlias = "_Score | Word"
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


Resource: TypeAlias = "_Resource | Word"
Ore = _Resource("Ore")
Gas = _Resource("Gas")
OreAndGas = _Resource("OreAndGas")


class _AllyStatus(_Unique):
    pass


AllyStatus: TypeAlias = "_AllyStatus | Word"
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

AllyStatusDict = {Enemy: 0, Ally: 1, AlliedVictory: 2}

ComparisonDict = {AtLeast: 0, AtMost: 1, Exactly: 10}

ModifierDict = {SetTo: 7, Add: 8, Subtract: 9}

OrderDict = {Move: 0, Patrol: 1, Attack: 2}

PlayerDict = {
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

PropStateDict = {Enable: 4, Disable: 5, Toggle: 6}

ResourceDict = {Ore: 0, Gas: 1, OreAndGas: 2}

ScoreDict = {
    Total: 0,
    Units: 1,
    Buildings: 2,
    UnitsAndBuildings: 3,
    Kills: 4,
    Razings: 5,
    KillsAndRazings: 6,
    Custom: 7,
}

SwitchActionDict = {Set: 4, Clear: 5, Toggle: 6, Random: 11}

SwitchStateDict = {Set: 2, Cleared: 3}

Unique = TypeVar("Unique", bound=_Unique)
T = TypeVar("T", int, "EUDVariable", "ConstExpr")


@overload
def _EncodeConst(t: str, d: dict[_Unique, int], s: Unique | ExprProxy[Unique]) -> int:
    ...


@overload
def _EncodeConst(t: str, d: dict[_Unique, int], s: T) -> T:
    ...


@overload
def _EncodeConst(t: str, d: dict[_Unique, int], s: ExprProxy[T]) -> T:
    ...


def _EncodeConst(t, d, s):
    s = ut.unProxy(s)
    try:
        return d[s]
    except (KeyError, TypeError):  # unhashable type
        if isinstance(s, _Unique):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, t))
        return s


@overload
def EncodeAllyStatus(s: "_AllyStatus | ExprProxy[_AllyStatus]", issueError: bool = False) -> int:
    ...


@overload
def EncodeAllyStatus(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeAllyStatus(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodeAllyStatus(s, issueError=False):
    """Convert [Enemy, Ally, AlliedVictory] to number [0, 1, 2]."""
    return _EncodeConst("AllyStatus", AllyStatusDict, s)


@overload
def EncodeComparison(s: _Comparison | ExprProxy[_Comparison], issueError: bool = False) -> int:
    ...


@overload
def EncodeComparison(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeComparison(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodeComparison(s, issueError=False):
    """Convert [AtLeast, AtMost, Exactly] to number [0, 1, 10]."""
    return _EncodeConst("Comparison", ComparisonDict, s)


@overload
def EncodeModifier(s: _Modifier | ExprProxy[_Modifier], issueError: bool = False) -> int:
    ...


@overload
def EncodeModifier(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeModifier(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodeModifier(s, issueError=False):
    """Convert [SetTo, Add, Subtract] to number [7, 8, 9]."""
    return _EncodeConst("Modifier", ModifierDict, s)


@overload
def EncodeOrder(s: _Order | ExprProxy[_Order], issueError: bool = False) -> int:
    ...


@overload
def EncodeOrder(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeOrder(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodeOrder(s, issueError=False):
    """Convert [Move, Patrol, Attack] to number [0, 1, 2]."""
    return _EncodeConst("Order", OrderDict, s)


@overload
def EncodePlayer(s: _Player | ExprProxy[_Player], issueError: bool = False) -> int:
    ...


@overload
def EncodePlayer(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodePlayer(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodePlayer(s, issueError=False):
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
def EncodePropState(s: _PropState | ExprProxy[_PropState], issueError: bool = False) -> int:
    ...


@overload
def EncodePropState(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodePropState(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodePropState(s, issueError=False):
    """Convert [Enable, Disable, Toogle] to number [4, 5, 6]"""
    return _EncodeConst("PropState", PropStateDict, s)


@overload
def EncodeResource(s: _Resource | ExprProxy[_Resource], issueError: bool = False) -> int:
    ...


@overload
def EncodeResource(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeResource(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodeResource(s, issueError=False):
    """Convert [Ore, Gas, OreAndGas] to [0, 1, 2]"""
    return _EncodeConst("Resource", ResourceDict, s)


@overload
def EncodeScore(s: _Score | ExprProxy[_Score], issueError: bool = False) -> int:
    ...


@overload
def EncodeScore(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeScore(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodeScore(s, issueError=False):
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
    return _EncodeConst("Score", ScoreDict, s)


@overload
def EncodeSwitchAction(
    s: _SwitchAction | ExprProxy[_SwitchAction], issueError: bool = False
) -> int:
    ...


@overload
def EncodeSwitchAction(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeSwitchAction(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodeSwitchAction(s, issueError=False):
    """Convert [Set, Clear, Toogle, Random] to [4, 5, 6, 11]."""
    return _EncodeConst("SwitchAction", SwitchActionDict, s)


@overload
def EncodeSwitchState(s: _SwitchState | ExprProxy[_SwitchState], issueError: bool = False) -> int:
    ...


@overload
def EncodeSwitchState(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeSwitchState(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodeSwitchState(s, issueError=False):
    """Convert [Set, Cleared] to [2, 3]."""
    return _EncodeConst("_SwitchState", SwitchStateDict, s)


@overload
def EncodeCount(s: _Count | ExprProxy[_Count], issueError: bool = False) -> int:
    ...


@overload
def EncodeCount(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeCount(s: ExprProxy[T], issueError: bool = False) -> T:
    ...


def EncodeCount(s, issueError=False):
    """Convert [All, (other numbers)] to number [0, (as-is)]."""
    s = ut.unProxy(s)
    if s is All:
        return 0
    elif isinstance(s, _Unique):
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, "count"))
    return s


# ========================


def EncodeProperty(
    prop: UnitProperty | bytes | ExprProxy[UnitProperty | bytes], issueError: bool = False
) -> int:
    prop = ut.unProxy(prop)
    return GetPropertyIndex(prop)
