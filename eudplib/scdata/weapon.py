# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeWeapon
from ..localize import _
from .offsetmap import ArrayEnumMember, ArrayMember, EPDOffsetMap, Flag
from .offsetmap import MemberKind as Mk


class TargetFlags(ArrayEnumMember):
    __slots__ = ()
    Air = Flag(0x001)
    Ground = Flag(0x002)
    Mechanical = Flag(0x004)
    Organic = Flag(0x008)
    NonBuilding = Flag(0x010)
    NonRobotic = Flag(0x020)
    Terrain = Flag(0x040)
    OrganicOrMechanical = Flag(0x080)
    PlayerOwned = Flag(0x100)  #
    "Can target your own unit, used by Consume"


class Weapon(ConstType, EPDOffsetMap):
    __slots__ = ()
    label = ArrayMember(0x6572E0, Mk.STATTEXT)
    flingy = ArrayMember(0x656CA8, Mk.FLINGY)
    # specialAttack = ArrayMember(0x6573E8, Mk.BYTE)
    # special attack is for reference only (unused)
    targetFlags = TargetFlags(0x657998, Mk.WORD)
    # can't use name 'range' because it's a python keyword
    minRange = ArrayMember(0x656A18, Mk.DWORD)
    maxRange = ArrayMember(0x657470, Mk.DWORD)
    upgrade = ArrayMember(0x6571D0, Mk.UPGRADE)
    damageType = ArrayMember(0x657258, Mk.DAMAGE_TYPE)
    behavior = ArrayMember(0x656670, Mk.WEAPON_BEHAVIOR)
    "Fly and follow target, appear on target unit, etc."
    removeAfter = ArrayMember(0x657040, Mk.BYTE)
    explosionType = ArrayMember(0x6566F8, Mk.EXPLOSION_TYPE)
    splashInnerRadius = ArrayMember(0x656888, Mk.WORD)
    splashMiddleRadius = ArrayMember(0x6570C8, Mk.WORD)
    splashOuterRadius = ArrayMember(0x657780, Mk.WORD)
    damage = ArrayMember(0x656EB0, Mk.WORD)
    damageBonus = ArrayMember(0x657678, Mk.WORD)
    cooldown = ArrayMember(0x656FB8, Mk.BYTE)
    damageFactor = ArrayMember(0x6564E0, Mk.BYTE)
    "aka 'missile count'"
    attackAngle = ArrayMember(0x656990, Mk.BYTE)
    launchSpin = ArrayMember(0x657888, Mk.BYTE)
    forwardOffset = graphicXOffset = ArrayMember(0x657910, Mk.BYTE)
    verticalOffset = graphicYOffset = ArrayMember(0x656C20, Mk.BYTE)
    targetErrorMessage = ArrayMember(0x656568, Mk.STATTEXT)
    icon = ArrayMember(0x656780, Mk.ICON)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeWeapon(initval))
