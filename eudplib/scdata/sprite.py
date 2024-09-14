# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeSprite
from ..localize import _
from .offsetmap import ArrayMember, EPDOffsetMap
from .offsetmap import MemberKind as Mk


class Sprite(ConstType, EPDOffsetMap):
    __slots__ = ()
    # Read only data skipped
    image = ArrayMember(0x666160, Mk.IMAGE)
    # hpBarSize = ArrayMember(0x665E50, Mk.BYTE)
    # hpBarSize starts on Sprites.dat ID 130
    # unknownFlag = ArrayMember(0x666570, Mk.BYTE)
    isVisible = ArrayMember(0x665C48, Mk.BOOL)
    # selectionCircle = ArrayMember(0x665AC0, Mk.BYTE)
    # selectionCircle and selectionVerticalOffset start on Sprites.dat ID 130
    # selectionVerticalOffset = ArrayMember(0x665FD8, Mk.BYTE)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeSprite(initval))
