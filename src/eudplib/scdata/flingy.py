# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from typing import ClassVar

from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeFlingy
from ..core.rawtrigger.typehint import _Flingy
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
    sprite: ClassVar = SpriteMember("array", 0x6CA318)
    topSpeed: ClassVar = DwordMember("array", 0x6C9EF8)
    acceleration: ClassVar = WordMember("array", 0x6C9C78)
    haltDistance: ClassVar = DwordMember("array", 0x6C9930)
    turnSpeed: ClassVar = ByteMember("array", 0x6C9E20)
    turnRadius = turnSpeed
    # unused: ClassVar = ByteMember("array", 0x6CA240)
    movementControl: ClassVar = MovementControlMember("array", 0x6C9858)

    @ut.classproperty
    def range(self):
        return (0, 208, 1)

    @classmethod
    def cast(cls, _from: _Flingy):
        if isinstance(_from, ConstType) and not isinstance(_from, cls):
            raise ut.EPError(_('"{}" is not a {}').format(_from, cls.__name__))
        return super().cast(_from)

    def __init__(self, initval: _Flingy) -> None:
        super().__init__(EncodeFlingy(initval))
