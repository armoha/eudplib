#!/usr/bin/python
# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import strenc
from .member import Member, MemberKind, UpgradeDataMember
from .scdataobject import SCDataObject


class UpgradeData(SCDataObject):
    mineralCostBase = Member(0x656740, MemberKind.WORD)  # noqa: N815
    mineralCostFactor = Member(0x6559C0, MemberKind.WORD)  # noqa: N815
    gasCostBase = Member(0x655840, MemberKind.WORD)  # noqa: N815
    gasCostFactor = Member(0x6557C0, MemberKind.WORD)  # noqa: N815
    timeCostBase = Member(0x655B80, MemberKind.WORD)  # noqa: N815
    timeCostFactor = Member(0x655940, MemberKind.WORD)  # noqa: N815
    requirementOffset = Member(0x6558C0, MemberKind.WORD)  # noqa: N815
    icon = Member(0x655AC0, MemberKind.WORD)
    label = Member(0x655A40, MemberKind.WORD)
    race = Member(0x655BFC, MemberKind.BYTE)
    maxLevel = Member(0x655700, MemberKind.BYTE)  # noqa: N815
    broodWarFlag = Member(0x655B3C, MemberKind.BYTE)  # noqa: N815

    def __init__(self, index):
        super().__init__(strenc.EncodeUpgrade(index))


UpgradeDataMember._data_object_type = UpgradeData
