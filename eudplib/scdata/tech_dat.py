#!/usr/bin/python
# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import strenc
from .member import Member, MemberKind, TechDataMember
from .scdataobject import SCDataObject


class TechData(SCDataObject):
    mineralCost = Member(0x656248, MemberKind.WORD)  # noqa: N815
    gasCost = Member(0x6561F0, MemberKind.WORD)  # noqa: N815
    timeCost = Member(0x6563D8, MemberKind.WORD)  # noqa: N815
    energyCost = Member(0x656380, MemberKind.WORD)  # noqa: N815
    # ??? = Member(0x656198, MemberKind.WORD)
    requirementOffset = Member(0x6562F8, MemberKind.WORD)  # noqa: N815
    icon = Member(0x656430, MemberKind.WORD)
    label = Member(0x6562A0, MemberKind.WORD)
    race = Member(0x656488, MemberKind.BYTE)
    researched = Member(0x656350, MemberKind.BYTE)  # UNUSED?
    broodWarFlag = Member(0x6564B4, MemberKind.BYTE)  # noqa: N815

    def __init__(self, index):
        super().__init__(strenc.EncodeUpgrade(index))


TechDataMember._data_object_type = TechData
