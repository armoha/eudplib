# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeUnitOrder
from ..core.rawtrigger.typehint import _UnitOrder
from ..localize import _
from .offsetmap import (
    AnimationMember,
    BoolMember,
    EPDOffsetMap,
    IconMember,
    StatTextMember,
    TechMember,
    UnitOrderMember,
    WeaponMember,
    WordMember,
)


class UnitOrder(EPDOffsetMap, ConstType):
    __slots__ = ()
    label = StatTextMember("array", 0x665280)
    useWeaponTargeting = BoolMember("array", 0x664B00)
    # secondaryOrder = BoolMember("array", 0x665940)
    # secondary order is for reference only (unused)
    # nonSubunit = BoolMember("array", 0x665A00)
    # non subunit is for reference only (unused)
    subunitInheritance = BoolMember("array", 0x664A40)
    "when main unit receives the order, gives it to subunit as well"
    # subunitCanUse = BoolMember("array", 0x6657C0)
    # subunit can use is for reference only (unused)
    canBeInterrupted = BoolMember("array", 0x665040)
    canBeLifted = BoolMember("array", 0x665100)
    "if a movement-type order, sets/clears Lifted (0x20) cunit movement flag"
    canBeQueued = BoolMember("array", 0x665700)
    disablingKeepsTarget = BoolMember("array", 0x6651C0)
    "does not clear order target unit when frozen by lockdown/stasis/maelstrom"
    canBeObstructed = BoolMember("array", 0x6654C0)
    fleeable = BoolMember("array", 0x664C80)
    "order can be interrupted by unit fleeing from hit reaction"
    # requireMoving = BoolMember("array", 0x664BC0)
    # require moving is for reference only (unused)
    weapon = WeaponMember("array", 0x665880)
    techUsed = TechMember("array", 0x664E00)
    animation = AnimationMember("array", 0x664D40)
    icon = IconMember("array", 0x664EC0)
    requirementOffset = WordMember("array", 0x665580)
    obscuredOrder = UnitOrderMember("array", 0x665400)

    @ut.classproperty
    def range(self):
        return (0, 188, 1)

    @classmethod
    def cast(cls, _from: _UnitOrder):
        if isinstance(_from, ConstType) and not isinstance(_from, cls):
            raise ut.EPError(_('"{}" is not a {}').format(_from, cls.__name__))
        return super().cast(_from)

    def __init__(self, initval: _UnitOrder) -> None:
        super().__init__(EncodeUnitOrder(initval))
