#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeUnitOrder
from ..localize import _
from .offsetmap import ArrayMember, EPDOffsetMap
from .offsetmap import MemberKind as Mk


class UnitOrder(ConstType, EPDOffsetMap):
    __slots__ = ()
    label = ArrayMember(0x665280, Mk.STATTEXT)
    useWeaponTargeting = ArrayMember(0x664B00, Mk.BOOL)
    # secondaryOrder = ArrayMember(0x665940, Mk.BOOL)
    # secondary order is for reference only (unused)
    # nonSubunit = ArrayMember(0x665A00, Mk.BOOL)
    # non subunit is for reference only (unused)
    subunitInheritance = ArrayMember(0x664A40, Mk.BOOL)
    "when main unit receives the order, gives it to subunit as well"
    # subunitCanUse = ArrayMember(0x6657C0, Mk.BOOL)
    # subunit can use is for reference only (unused)
    canBeInterrupted = ArrayMember(0x665040, Mk.BOOL)
    canBeLifted = ArrayMember(0x665100, Mk.BOOL)
    "if a movement-type order, sets/clears Lifted (0x20) cunit movement flag"
    canBeQueued = ArrayMember(0x665700, Mk.BOOL)
    disablingKeepsTarget = ArrayMember(0x6651C0, Mk.BOOL)
    "does not clear order target unit when frozen by lockdown/stasis/maelstrom"
    canBeObstructed = ArrayMember(0x6654C0, Mk.BOOL)
    fleeable = ArrayMember(0x664C80, Mk.BOOL)
    "order can be interrupted by unit fleeing from hit reaction"
    # requireMoving = ArrayMember(0x664BC0, Mk.BOOL)
    # require moving is for reference only (unused)
    weapon = ArrayMember(0x665880, Mk.WEAPON)
    techUsed = ArrayMember(0x664E00, Mk.TECH)
    animation = ArrayMember(0x664D40, Mk.ANIMATION)
    icon = ArrayMember(0x664EC0, Mk.ICON)
    requirementOffset = ArrayMember(0x665580, Mk.WORD)
    obscuredOrder = ArrayMember(0x665400, Mk.UNIT_ORDER)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeUnitOrder(initval))
