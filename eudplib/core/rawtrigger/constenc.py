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

from ... import utils as ut
from ...localize import _
from ..mapdata import GetPropertyIndex


class _Unique:
    def __init__(self, name: str) -> None:
        self._name: str = name

    def __repr__(self) -> str:
        return self._name

    def __str__(self) -> str:
        return repr(self)


class Player(_Unique):
    pass


class PlayerGroup(Player):
    pass


P1 = Player("P1")
P2 = Player("P2")
P3 = Player("P3")
P4 = Player("P4")
P5 = Player("P5")
P6 = Player("P6")
P7 = Player("P7")
P8 = Player("P8")
P9 = Player("P9")
P10 = Player("P10")
P11 = Player("P11")
P12 = Player("P12")
Player1 = Player("Player1")
Player2 = Player("Player2")
Player3 = Player("Player3")
Player4 = Player("Player4")
Player5 = Player("Player5")
Player6 = Player("Player6")
Player7 = Player("Player7")
Player8 = Player("Player8")
Player9 = Player("Player9")
Player10 = Player("Player10")
Player11 = Player("Player11")
Player12 = Player("Player12")
CurrentPlayer = Player("CurrentPlayer")
Foes = PlayerGroup("Foes")
Allies = PlayerGroup("Allies")
NeutralPlayers = PlayerGroup("NeutralPlayers")
AllPlayers = PlayerGroup("AllPlayers")
Force1 = PlayerGroup("Force1")
Force2 = PlayerGroup("Force2")
Force3 = PlayerGroup("Force3")
Force4 = PlayerGroup("Force4")
NonAlliedVictoryPlayers = PlayerGroup("NonAlliedVictoryPlayers")


class AllyStatus(_Unique):
    pass


All = AllyStatus("All")
Enemy = AllyStatus("Enemy")
Ally = AllyStatus("Ally")
AlliedVictory = AllyStatus("AlliedVictory")


class Comparison(_Unique):
    pass


AtLeast = Comparison("AtLeast")
AtMost = Comparison("AtMost")
Exactly = Comparison("Exactly")


class Modifier(_Unique):
    pass


SetTo = Modifier("SetTo")
Add = Modifier("Add")
Subtract = Modifier("Subtract")


class Order(_Unique):
    pass


Move = Order("Move")
Patrol = Order("Patrol")
Attack = Order("Attack")


class PropState(_Unique):
    pass


Enable = PropState("Enable")
Disable = PropState("Disable")
Toggle = PropState("Toggle")


class Resource(_Unique):
    pass


Ore = Resource("Ore")
Gas = Resource("Gas")
OreAndGas = Resource("OreAndGas")


class Score(_Unique):
    pass


class _KillsSpecialized(Score):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._internalf: Callable

    def __call__(self, a, b, c, d):
        return self._internalf(a, b, c, d)


Total = Score("Total")
Units = Score("Units")
Buildings = Score("Buildings")
UnitsAndBuildings = Score("UnitsAndBuildings")
# Name 'Kills' is used for both condition type and score type.
# To resolve conflict, we initialize Kills differently from others.
Kills = _KillsSpecialized("Kills")
Razings = Score("Razings")
KillsAndRazings = Score("KillsAndRazings")
Custom = Score("Custom")


class SwitchState(_Unique):
    pass


Set = SwitchState("Set")
Clear = SwitchState("Clear")
Random = SwitchState("Random")
Cleared = SwitchState("Cleared")

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


def _EncodeConst(t, d, s, issueError):
    s = ut.unProxy(s)
    try:
        return d[s]
    except (KeyError, TypeError):  # unhashable type
        if isinstance(s, _Unique):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, t))
        return s


def EncodeAllyStatus(s, issueError=False):
    """
    Convert [Enemy, Ally, AlliedVictory] to number [0, 1, 2].
    """
    return _EncodeConst("AllyStatus", AllyStatusDict, s, issueError)


def EncodeComparison(s, issueError=False):
    """
    Convert [AtLeast, AtMost, Exactly] to number [0, 1, 10].
    """
    return _EncodeConst("Comparison", ComparisonDict, s, issueError)


def EncodeModifier(s, issueError=False):
    """
    Convert [SetTo, Add, Subtract] to number [7, 8, 9].
    """
    return _EncodeConst("Modifier", ModifierDict, s, issueError)


def EncodeOrder(s, issueError=False):
    """
    Convert [Move, Patrol, Attack] to number [0, 1, 2].
    """
    return _EncodeConst("Order", OrderDict, s, issueError)


def EncodePlayer(s, issueError=False):
    """
    Convert player identifier to corresponding number.

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
    return _EncodeConst("Player", PlayerDict, s, issueError)


def EncodePropState(s, issueError=False):
    """
    Convert [Enable, Disable, Toogle] to number [4, 5, 6]
    """
    return _EncodeConst("PropState", PropStateDict, s, issueError)


def EncodeResource(s, issueError=False):
    """
    Convert [Ore, Gas, OreAndGas] to [0, 1, 2]
    """
    return _EncodeConst("Resource", ResourceDict, s, issueError)


def EncodeScore(s, issueError=False):
    """
    Convert score type identifier to number.

    ================= ========
        Score type     Number
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
    return _EncodeConst("Score", ScoreDict, s, issueError)


def EncodeSwitchAction(s, issueError=False):
    """
    Convert [Set, Clear, Toogle, Random] to [4, 5, 6, 11].
    """
    return _EncodeConst("SwitchAction", SwitchActionDict, s, issueError)


def EncodeSwitchState(s, issueError=False):
    """
    Convert [Set, Cleared] to [2, 3].
    """
    return _EncodeConst("SwitchState", SwitchStateDict, s, issueError)


def EncodeCount(s, issueError=False):
    """
    Convert [All, (other numbers)] to number [0, (as-is)].
    """
    s = ut.unProxy(s)
    if s is All:
        return 0
    elif isinstance(s, _Unique):
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, "count"))
    return s


# ========================


def EncodeProperty(prop, issueError=False):
    return GetPropertyIndex(prop)
