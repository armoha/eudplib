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
    damage = Member(0x656EB0, MemberKind.WORD)
    cooldown = Member(0x656EBC, MemberKind.WORD)

    def __init__(self, index):
        super().__init__(strenc.EncodeWeapon(index))

WeaponDataMember._data_object_type = WeaponData
