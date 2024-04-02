#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import strenc
from .member import Member, MemberKind, WeaponDataMember
from .scdataobject import SCDataObject


class WeaponData(SCDataObject):
    label = Member(0x6572E0, MemberKind.WORD)
    graphic = flingy = Member(0x656CA8, MemberKind.FLINGY)
    # special attack is for reference only?
    # specialAttack = Member(0x6573E8, MemberKind.BYTE)
    targetFlags = Member(0x657998, MemberKind.DWORD)  # noqa: N815
    # can't use range because it's a python keyword
    minRange = Member(0x656A18, MemberKind.DWORD)  # noqa: N815
    maxRange = Member(0x6573E8, MemberKind.DWORD)  # noqa: N815
    upgrade = upgradeID = Member(0x6571D0, MemberKind.BYTE)  # noqa: N815
    damageType = Member(0x657258, MemberKind.BYTE)  # noqa: N815
    # Fly and follow target, appear on target unit, etc.
    behavior = Member(0x656670, MemberKind.BYTE)
    removeAfter = Member(0x657040, MemberKind.BYTE)  # noqa: N815
    explosionType = Member(0x6566F8, MemberKind.BYTE)  # noqa: N815
    splashInnerRadius = Member(0x656888, MemberKind.WORD)  # noqa: N815
    splashMiddleRadius = Member(0x6570C8, MemberKind.WORD)  # noqa: N815
    splashOuterRadius = Member(0x657780, MemberKind.WORD)  # noqa: N815
    damage = Member(0x656EB0, MemberKind.WORD)
    damageBonus = Member(0x657678, MemberKind.WORD)  # noqa: N815
    cooldown = Member(0x656EBC, MemberKind.BYTE)
    damageFactor = Member(0x6564E0, MemberKind.BYTE)  # noqa: N815
    attackAngle = Member(0x656990, MemberKind.BYTE)  # noqa: N815
    launchSpin = Member(0x657888, MemberKind.BYTE)  # noqa: N815
    forwardOffset = graphicXOffset = Member(0x657910, MemberKind.BYTE)  # noqa: N815
    verticalOffset = graphicYOffset = Member(0x656C20, MemberKind.BYTE)  # noqa: N815
    targetErrorMessage = Member(0x656568, MemberKind.WORD)  # noqa: N815
    icon = Member(0x656780, MemberKind.WORD)

    def __init__(self, index):
        super().__init__(strenc.EncodeWeapon(index))


WeaponDataMember._data_object_type = WeaponData
