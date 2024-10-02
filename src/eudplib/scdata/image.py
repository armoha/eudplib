# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeImage
from ..localize import _
from .offsetmap import ArrayMember, EPDOffsetMap
from .offsetmap import MemberKind as Mk


class Image(EPDOffsetMap, ConstType):
    __slots__ = ()
    # Read only data skipped
    # grpFile = ArrayMember(0x668AA0, Mk.DWORD)
    isTurnable = graphicTurn = ArrayMember(0x66E860, Mk.BOOL)
    isClickable = ArrayMember(0x66C150, Mk.BOOL)
    useFullIscript = ArrayMember(0x66D4D8, Mk.BOOL)
    drawIfCloaked = ArrayMember(0x667718, Mk.BOOL)
    drawingFunction = ArrayMember(0x669E28, Mk.DRAWING_FUNCION)
    # FIXME: Add UnsupportedMember?
    # remapping = ArrayMember(0x669A40, Mk.BYTE)
    # Remapping table is skipped because it doesn't work in SC:R
    iscript = ArrayMember(0x66EC48, Mk.ISCRIPT)
    # shieldsOverlay = ArrayMember(0x66C538, Mk.DWORD)
    # attackOverlay = ArrayMember(0x66B1B0, Mk.DWORD)
    # damageOverlay = ArrayMember(0x66A210, Mk.DWORD)
    # specialOverlay = ArrayMember(0x667B00, Mk.DWORD)
    # landingDustOverlay = ArrayMember(0x666778, Mk.DWORD)
    # liftOffDustOverlay = ArrayMember(0x66D8C0, Mk.DWORD)

    @ut.classproperty
    def range(self):
        return (0, 998, 1)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('"{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeImage(initval))
