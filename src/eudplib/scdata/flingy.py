# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeFlingy
from ..localize import _
from .offsetmap import ArrayMember, EPDOffsetMap
from .offsetmap import MemberKind as Mk


class Flingy(EPDOffsetMap, ConstType):
    __slots__ = ()
    sprite = ArrayMember(0x6CA318, Mk.SPRITE)
    topSpeed = ArrayMember(0x6C9EF8, Mk.DWORD)
    acceleration = ArrayMember(0x6C9C78, Mk.WORD)
    haltDistance = ArrayMember(0x6C9930, Mk.DWORD)
    turnSpeed = turnRadius = ArrayMember(0x6C9E20, Mk.BYTE)
    # unused = ArrayMember(0x6CA240, Mk.BYTE)
    movementControl = ArrayMember(0x6C9858, Mk.MOVEMENT_CONTROL)

    @ut.classproperty
    def range(self):
        return (0, 208, 1)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('"{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeFlingy(initval))
