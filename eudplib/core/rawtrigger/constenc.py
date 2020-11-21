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

from ..mapdata import GetPropertyIndex
from ... import utils as ut
from ...localize import _

isMemDestStrict = True


def EP_SetMemDestStrictMode(mode):
    global isMemDestStrict
    isMemDestStrict = mode


class _Unique:
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return "_Unique(%s)" % self._name

    def __str__(self):
        return repr(self)


class _KillsSpecialized:
    def __call__(self, a, b, c, d):
        return self._internalf(a, b, c, d)


All = _Unique("All")
Enemy = _Unique("Enemy")
Ally = _Unique("Ally")
AlliedVictory = _Unique("AlliedVictory")
AtLeast = _Unique("AtLeast")
AtMost = _Unique("AtMost")
Exactly = _Unique("Exactly")
SetTo = _Unique("SetTo")
Add = _Unique("Add")
Subtract = _Unique("Subtract")
Move = _Unique("Move")
Patrol = _Unique("Patrol")
Attack = _Unique("Attack")
P1 = _Unique("P1")
P2 = _Unique("P2")
P3 = _Unique("P3")
P4 = _Unique("P4")
P5 = _Unique("P5")
P6 = _Unique("P6")
P7 = _Unique("P7")
P8 = _Unique("P8")
P9 = _Unique("P9")
P10 = _Unique("P10")
P11 = _Unique("P11")
P12 = _Unique("P12")
Player1 = _Unique("Player1")
Player2 = _Unique("Player2")
Player3 = _Unique("Player3")
Player4 = _Unique("Player4")
Player5 = _Unique("Player5")
Player6 = _Unique("Player6")
Player7 = _Unique("Player7")
Player8 = _Unique("Player8")
Player9 = _Unique("Player9")
Player10 = _Unique("Player10")
Player11 = _Unique("Player11")
Player12 = _Unique("Player12")
CurrentPlayer = _Unique("CurrentPlayer")
Foes = _Unique("Foes")
Allies = _Unique("Allies")
NeutralPlayers = _Unique("NeutralPlayers")
AllPlayers = _Unique("AllPlayers")
Force1 = _Unique("Force1")
Force2 = _Unique("Force2")
Force3 = _Unique("Force3")
Force4 = _Unique("Force4")
NonAlliedVictoryPlayers = _Unique("NonAlliedVictoryPlayers")
Enable = _Unique("Enable")
Disable = _Unique("Disable")
Toggle = _Unique("Toggle")
Ore = _Unique("Ore")
Gas = _Unique("Gas")
OreAndGas = _Unique("OreAndGas")
Total = _Unique("Total")
Units = _Unique("Units")
Buildings = _Unique("Buildings")
UnitsAndBuildings = _Unique("UnitsAndBuildings")

# Name 'Kills' is used for both condition type and score type.
# To resolve conflict, we initialize Kills differently from others.
Kills = _KillsSpecialized()
Razings = _Unique("Razings")
KillsAndRazings = _Unique("KillsAndRazings")
Custom = _Unique("Custom")
Set = _Unique("Set")
Clear = _Unique("Clear")
Random = _Unique("Random")
Cleared = _Unique("Cleared")

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
        return d.get(s, s)
    except TypeError:  # unhashable type
        if issueError and isinstance(s, _Unique):
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
    else:
        return s


# ========================


def EncodeProperty(prop, issueError=False):
    return GetPropertyIndex(prop)
