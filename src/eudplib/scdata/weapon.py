# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeWeapon
from ..core.rawtrigger.typehint import Weapon as _Weapon
from ..localize import _
from .offsetmap import (
    ByteMember,
    DamageTypeMember,
    DwordMember,
    EPDOffsetMap,
    ExplosionTypeMember,
    Flag,
    FlingyMember,
    IconMember,
    StatTextMember,
    UpgradeMember,
    WeaponBehaviorMember,
    WordEnumMember,
    WordMember,
)


class TargetFlags(WordEnumMember):
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


class Weapon(EPDOffsetMap, ConstType):
    __slots__ = ()
    label = StatTextMember("array", 0x6572E0)
    flingy = FlingyMember("array", 0x656CA8)
    # specialAttack = ByteMember("array", 0x6573E8)
    # special attack is for reference only (unused)
    targetFlags = TargetFlags("array", 0x657998)
    # can't use name 'range' because it's a python keyword
    minRange = DwordMember("array", 0x656A18)
    maxRange = DwordMember("array", 0x657470)
    upgrade = UpgradeMember("array", 0x6571D0)
    damageType = DamageTypeMember("array", 0x657258)
    behavior = WeaponBehaviorMember("array", 0x656670)
    "Fly and follow target, appear on target unit, etc."
    removeAfter = ByteMember("array", 0x657040)
    explosionType = ExplosionTypeMember("array", 0x6566F8)
    splashInnerRadius = WordMember("array", 0x656888)
    splashMiddleRadius = WordMember("array", 0x6570C8)
    splashOuterRadius = WordMember("array", 0x657780)
    damage = WordMember("array", 0x656EB0)
    damageBonus = WordMember("array", 0x657678)
    cooldown = ByteMember("array", 0x656FB8)
    damageFactor = ByteMember("array", 0x6564E0)
    "aka 'missile count'"
    attackAngle = ByteMember("array", 0x656990)
    launchSpin = ByteMember("array", 0x657888)
    forwardOffset = graphicXOffset = ByteMember("array", 0x657910)
    verticalOffset = graphicYOffset = ByteMember("array", 0x656C20)
    targetErrorMessage = StatTextMember("array", 0x656568)
    icon = IconMember("array", 0x656780)

    @ut.classproperty
    def range(self):
        return (0, 129, 1)

    @classmethod
    def cast(cls, _from: _Weapon):
        if isinstance(_from, ConstType) and not isinstance(_from, cls):
            raise ut.EPError(_('"{}" is not a {}').format(_from, cls.__name__))
        return super().cast(_from)

    def __init__(self, initval: _Weapon) -> None:
        super().__init__(EncodeWeapon(initval))
