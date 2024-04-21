#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import strenc
from .member import Member, MemberKind, UnitOrderDataMember
from .scdataobject import SCDataObject


class UnitOrderData(SCDataObject):
    label = Member(0x665280, MemberKind.WORD)
    useWeaponTargeting = Member(0x664B00, MemberKind.BOOL)  # noqa: N815
    # secondaryOrder = Member(0x665940, MemberKind.BYTE)
    # nonSubUnit = Member(0x665A00, MemberKind.BYTE)
    # ??? = Member(0x664A40, MemberKind.BYTE)
    # subUnitcanUse = Member(0x6657C0, MemberKind.BYTE)
    canBeInterrupted = Member(0x665040, MemberKind.BOOL)  # noqa: N815
    # ??? = Member(0x665100, MemberKind.BYTE)
    canBeQueued = Member(0x665700, MemberKind.BOOL)  # noqa: N815
    # ??? = Member(0x6651C0, MemberKind.BYTE)
    canBeObstructed = Member(0x6654C0, MemberKind.BOOL)  # noqa: N815
    # ??? = Member(0x664C80, MemberKind.BYTE)
    # requireMoving = Member(0x664BC0, MemberKind.BYTE)
    weapon = weaponID = Member(0x665880, MemberKind.BYTE)  # noqa: N815
    techUsed = Member(0x664E00, MemberKind.BYTE)  # noqa: N815
    animation = Member(0x664D40, MemberKind.BYTE)
    buttonIcon = Member(0x664EC0, MemberKind.WORD)  # noqa: N815
    requirementOffset = Member(0x665580, MemberKind.WORD)  # noqa: N815
    obscuredOrder = Member(0x665400, MemberKind.BYTE)  # noqa: N815

    def __init__(self, index):
        super().__init__(strenc.EncodeUnitOrder(index))


UnitOrderDataMember._data_object_type = UnitOrderData
