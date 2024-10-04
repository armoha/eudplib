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
from .offsetmap import (
    ByteMember,
    DwordMember,
    EPDOffsetMap,
    MovementControlMember,
    SpriteMember,
    WordMember,
)


class Flingy(EPDOffsetMap, ConstType):
    __slots__ = ()
    sprite = SpriteMember("array", 0x6CA318)
    topSpeed = DwordMember("array", 0x6C9EF8)
    acceleration = WordMember("array", 0x6C9C78)
    haltDistance = DwordMember("array", 0x6C9930)
    turnSpeed = turnRadius = ByteMember("array", 0x6C9E20)
    # unused = ByteMember("array", 0x6CA240)
    movementControl = MovementControlMember("array", 0x6C9858)

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
