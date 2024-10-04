# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from typing import ClassVar

from .. import utils as ut
from ..core.rawtrigger.constenc import EncodePlayer, PlayerDict, _Player
from ..core.rawtrigger.consttype import ConstType
from ..localize import _
from .offsetmap import ByteMember, DwordMember, EPDOffsetMap, MapStringMember


class TrgPlayer(EPDOffsetMap, _Player):
    """
    TrgPlayer is special in the sense that it is not directly related to game data;
    rather, it is intended to deal with various game state specific to players.
    e.g. the amount of gas a player has, can be accessed via TrgPlayer.
    """

    __slots__ = ()
    mineral: ClassVar = DwordMember("array", 0x57F0F0)
    ore = mineral
    gas: ClassVar = DwordMember("array", 0x57F120)
    cumulativeGas: ClassVar = DwordMember("array", 0x57F150)
    cumulativeMineral: ClassVar = DwordMember("array", 0x57F180)
    zergControlAvailable: ClassVar = DwordMember("array", 0x582144)
    zergControlUsed: ClassVar = DwordMember("array", 0x582174)
    zergControlMax: ClassVar = DwordMember("array", 0x5821A4)
    terranSupplyAvailable: ClassVar = DwordMember("array", 0x5821D4)
    terranSupplyUsed: ClassVar = DwordMember("array", 0x582204)
    terranSupplyMax: ClassVar = DwordMember("array", 0x582234)
    protossPsiAvailable: ClassVar = DwordMember("array", 0x582264)
    protossPsiUsed: ClassVar = DwordMember("array", 0x582294)
    protossPsiMax: ClassVar = DwordMember("array", 0x5822C4)
    unitColor: ClassVar = ByteMember("array", 0x581D76, stride=8)
    minimapColor: ClassVar = ByteMember("array", 0x581DD6)
    remainingGamePause: ClassVar = ByteMember("array", 0x58D718)  # length=8
    missionObjectives: ClassVar = MapStringMember("array", 0x58D6C4, stride=4)
    unitScore: ClassVar = DwordMember("array", 0x581E44)
    "Score for units produced"
    buildingScore: ClassVar = DwordMember("array", 0x582024)
    "Score for buildings produced"
    killScore: ClassVar = DwordMember("array", 0x581F04)
    razingScore: ClassVar = DwordMember("array", 0x582054)
    customScore: ClassVar = DwordMember("array", 0x5822F4)
    # scoreUnitTotal: ClassVar = ArrayMember(0x581ED4)
    # numOfFactoriesRazed: ClassVar = ArrayMember(0x582114) Kills for "Factories"
    # numOfBuildingsRazed: ClassVar = ArrayMember(0x581FF4) Kills for "Buildings"
    # numOfUnitsKilled: ClassVar = ArrayMember(0x581EA4) Kills for "Any Unit"
    # humanID: ClassVar = DwordMember("array", 0x57EE7C)
    # nationID: ClassVar = DwordMember("array", 0x57EEC0)
    # networkStatus: ClassVar = DwordMember("array", 0x57F0B8)
    # playerSlotType: ClassVar = ByteMember("array", 0x57F1B4)
    # playerSlotRace: ClassVar = ByteMember("array", 0x57F1C0)
    # sharedVision: ClassVar = DwordMember("array", 0x57F1EC)
    # colorMapping: ClassVar = DwordMember("array", 0x57F21C) length=8
    # singleplayerComputerRace: ClassVar = ByteMember("array", 0x57F267) length=8
    # hasLeftGame: ClassVar = ArrayMember(0x581D62, Mk.BOOL) length=8
    # selectionCircleColor: ClassVar = ByteMember("array", 0x581D6A)
    # ownedTotalUnitsScore: ClassVar = ArrayMember(0x581DE4)
    # ownedUnitsScore: ClassVar = ArrayMember(0x581E14)
    # numOfUnitsLost: ClassVar = ArrayMember(0x581E74) Deaths for "Any Unit"
    # scoreStructuresConstructedTotal: ClassVar = ArrayMember(0x581F34)
    # numOfBuildingsConstructed: ClassVar = ArrayMember(0x581F64)
    # numOfBuildingsOwned: ClassVar = ArrayMember(0x581F94)
    # numOfBuildingsLost: ClassVar = ArrayMember(0x581FC4) Deaths for "Buildings"
    # numOfFactoriesConstructed: ClassVar = ArrayMember(0x582084)
    # numOfFactoriesOwned: ClassVar = ArrayMember(0x5820B4)
    # numOfFactoriesLost: ClassVar = ArrayMember(0x5820E4) Deaths for "Factories"
    # larvaCount: ClassVar = ByteMember("array", 0x585474)
    # force: ClassVar = ByteMember("array", 0x58D5B0) length=8
    # allyStatus: ClassVar = ByteMember("array", 0x58D634)
    # victoryStatus: ClassVar = ByteMember("array", 0x58D700) length=8
    # startLocationPos: ClassVar = ArrayMember(0x58D720, Mk.POSITION) length=8
    # 0x58F442 Unknown Player Color Something length=8
    # triggerWaitTimer: ClassVar = DwordMember("array", 0x650980) length=8
    # 0x6D0F3C Replay Header - Player Bytes: Read Only
    # 0x6D0FD1 Replay Header - Player Entries: Read Only
    # 0x6D1181 Replay Header - Player Colors: Read Only length=8
    # 0x6D11A1 Replay Header - Player Force Data: Read Only length=8

    @ut.classproperty
    def range(self):
        return (0, 11, 1)

    @classmethod
    def cast(cls, _from):
        if isinstance(_from, ConstType) and not isinstance(_from, cls):
            raise ut.EPError(_('"{}" is not a {}').format(_from, cls.__name__))
        return super().cast(_from)

    def __init__(self, initval) -> None:
        super().__init__(EncodePlayer(initval))


# fmt: off
P1, P2, P3, P4 = TrgPlayer(0), TrgPlayer(1), TrgPlayer(2), TrgPlayer(3)
P5, P6, P7, P8 = TrgPlayer(4), TrgPlayer(5), TrgPlayer(6), TrgPlayer(7)
P9, P10, P11, P12 = TrgPlayer(8), TrgPlayer(9), TrgPlayer(10), TrgPlayer(11)
Player1, Player2, Player3, Player4 = P1, P2, P3, P4
Player5, Player6, Player7, Player8 = P5, P6, P7, P8
Player9, Player10, Player11, Player12 = P9, P10, P11, P12
CurrentPlayer = TrgPlayer(13)
Foes, Allies, NeutralPlayers = TrgPlayer(14), TrgPlayer(15), TrgPlayer(16)
AllPlayers = TrgPlayer(17)
Force1, Force2, Force3, Force4 = TrgPlayer(18), TrgPlayer(19), TrgPlayer(20), TrgPlayer(21)  # noqa: E501
NonAlliedVictoryPlayers = TrgPlayer(26)
PlayerDict.update({
    P1: 0, P2: 1, P3: 2, P4: 3,
    P5: 4, P6: 5, P7: 6, P8: 7,
    P9: 8, P10: 9, P11: 10, P12: 11,
    CurrentPlayer: 13,
    Foes: 14, Allies: 15, NeutralPlayers: 16,
    AllPlayers: 17,
    Force1: 18, Force2: 19, Force3: 20, Force4: 21,
    NonAlliedVictoryPlayers: 26,
})
# fmt: on
