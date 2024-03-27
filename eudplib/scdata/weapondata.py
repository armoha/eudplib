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
    damageFactor = Member(0x6564E0, MemberKind.BYTE)  # noqa: N815
    targetErrorMessage = Member(0x656568, MemberKind.WORD)  # noqa: N815
    behavior = Member(0x656670, MemberKind.BYTE)
    effect = Member(0x6566F8, MemberKind.BYTE)
    icon = Member(0x656780, MemberKind.WORD)
    splashInner = splashInnerRadius = Member(0x656888, MemberKind.WORD)  # noqa: N815
    attackAngle = Member(0x656990, MemberKind.WORD)  # noqa: N815
    minimumRange = minRange = Member(0x656A18, MemberKind.DWORD)  # noqa: N815
    graphicsYOffset = Member(0x656C20, MemberKind.BYTE)  # noqa: N815
    graphics = Member(0x656CA8, MemberKind.FLINGY)
    damage = Member(0x656EB0, MemberKind.WORD)
    cooldown = Member(0x656EBC, MemberKind.WORD)
    removeAfter = Member(0x657040, MemberKind.BYTE)  # noqa: N815
    splashMiddle = splashMiddleRadius = Member(0x6570C8, MemberKind.WORD)  # noqa: N815
    upgrade = upgradeID = Member(0x6571D0, MemberKind.BYTE)  # noqa: N815
    damageType = Member(0x657258, MemberKind.BYTE)  # noqa: N815
    label = Member(0x6572E0, MemberKind.WORD)
    # special attack is for reference only?
    # can't use range because it's a python keyword
    maxRange = Member(0x6573E8, MemberKind.DWORD)  # noqa: N815
    bonus = upgradeBonus = Member(0x657678, MemberKind.WORD)  # noqa: N815
    splashOuter = splashOuterRadius = Member(0x657780, MemberKind.WORD)  # noqa: N815
    launchSpin = Member(0x657888, MemberKind.BYTE)  # noqa: N815
    graphicsXOffset = Member(0x657910, MemberKind.BYTE)  # noqa: N815
    targetFlags = Member(0x657998, MemberKind.DWORD)  # noqa: N815

    def __init__(self, index):
        super().__init__(strenc.EncodeWeapon(index))


WeaponDataMember._data_object_type = WeaponData
