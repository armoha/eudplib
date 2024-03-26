#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import strenc
from .member import (
    FlingyDataMember,
    Member,
    MemberKind,
    UnitDataMember,
    UnitOrderDataMember,
    WeaponDataMember,
)
from .scdataobject import SCDataObject


class UnitData(SCDataObject):
    __slots__ = []
    maxHP = hitPoints = HP = Member(0x662350, MemberKind.DWORD)  # noqa: N815
    maxAirHits = Member(0x65FC18, MemberKind.BYTE)  # noqa: N815
    gas = gasCost = Member(0x65FD00, MemberKind.WORD)  # noqa: N815
    armor = Member(0x65FEC8, MemberKind.BYTE)
    whatSoundStart = Member(0x65FFB0, MemberKind.WORD)  # noqa: N815
    AIInternal = Member(0x660178, MemberKind.BYTE)
    mapString = Member(0x660260, MemberKind.WORD)  # noqa: N815
    buildTime = Member(0x660428, MemberKind.WORD)  # noqa: N815
    startDirection = Member(0x6605F0, MemberKind.BYTE)  # noqa: N815
    broodWarFlag = Member(0x6606D8, MemberKind.BYTE)  # noqa: N815
    subUnit = subUnit1 = UnitDataMember(0x6607C0)  # noqa: N815
    transportSpaceProvided = Member(0x660988, MemberKind.BYTE)  # noqa: N815
    # datRequirementOffset is not implemented yet.
    # subunit2 is unused
    shield = shields = Member(0x660E00, MemberKind.WORD)
    movementFlags = Member(0x660FC8, MemberKind.BYTE)  # noqa: N815
    constructionAnimation = Member(0x6610B0, MemberKind.BYTE)  # noqa: N815
    yesSoundEnd = Member(0x661440, MemberKind.WORD)  # noqa: N815
    stareditAvailabilityFlags = Member(0x661528, MemberKind.WORD)  # noqa: N815
    airWeapon = WeaponDataMember(0x6616E0)  # noqa: N815
    # unitDimensions is not implemented yet.
    pissedSoundEnd = Member(0x661EE8, MemberKind.WORD)  # noqa: N815
    readySound = Member(0x661FC0, MemberKind.WORD)  # noqa: N815
    rightClickAction = Member(0x662098, MemberKind.BYTE)  # noqa: N815
    sizeClass = Member(0x662180, MemberKind.BYTE)  # noqa: N815
    # AddonPlacement is not implemented yet becasue its beginning index isn't 0.
    buildingDimensions = Member(0x662860, MemberKind.POSITION)  # noqa: N815
    whatSoundEnd = Member(0x662BF0, MemberKind.WORD)  # noqa: N815
    seekRange = Member(0x662DB8, MemberKind.BYTE)  # noqa: N815
    computerInitAction = computerIdle = Member(0x662EA0, MemberKind.BYTE)  # noqa: N815
    portrait = Member(0x662F88, MemberKind.WORD)
    elevationLevel = Member(0x663150, MemberKind.BYTE)  # noqa: N815
    sightRange = Member(0x663238, MemberKind.BYTE)  # noqa: N815
    attackUnitOrder = UnitOrderDataMember(0x663320)  # noqa: N815
    buildScore = Member(0x663408, MemberKind.WORD)  # noqa: N815
    armorUpgrade = Member(0x6635D0, MemberKind.BYTE)  # noqa: N815
    groundWeapon = WeaponDataMember(0x6636B8)  # noqa: N815
    groupFlags = Member(0x6637A0, MemberKind.BYTE)  # noqa: N815
    mineralCost = Member(0x663888, MemberKind.WORD)  # noqa: N815
    attackMoveOrder = UnitOrderDataMember(0x663A50)  # noqa: N815
    pissedSoundStart = Member(0x663B38, MemberKind.WORD)  # noqa: N815
    yesSoundStart = Member(0x663C10, MemberKind.WORD)  # noqa: N815
    supplyUsed = Member(0x663CE8, MemberKind.BYTE)  # noqa: N815
    rank = Member(0x663DD0, MemberKind.BYTE)
    killScore = Member(0x663EB8, MemberKind.WORD)  # noqa: N815
    advancedFlags = Member(0x664080, MemberKind.DWORD)  # noqa: N815
    transportSpaceRequired = Member(0x664410, MemberKind.BYTE)  # noqa: N815
    flingy = FlingyDataMember(0x6644F8)
    maxGroundHits = Member(0x6645E0, MemberKind.BYTE)  # noqa: N815
    supplyProvided = Member(0x6646C8, MemberKind.BYTE)  # noqa: N815
    hasShields = Member(0x6647B0, MemberKind.BOOL)  # noqa: N815
    idleOrder = UnitOrderDataMember(0x664898)  # noqa: N815
    # infestationUnit is not implemented yet. (different beginning index)

    def __init__(self, index):
        super().__init__(strenc.EncodeUnit(index))

UnitDataMember._data_object_type = UnitData
