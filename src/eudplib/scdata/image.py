# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from typing import ClassVar

from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeImage
from ..core.rawtrigger.typehint import _Image
from ..localize import _
from .offsetmap import BoolMember, DrawingFunctionMember, EPDOffsetMap, IscriptMember


class Image(EPDOffsetMap, ConstType):
    __slots__ = ()
    # Read only data skipped
    # grpFile: ClassVar[ArrayMember] = ArrayMember(0x668AA0, Mk.DWORD)
    isTurnable: ClassVar[BoolMember] = BoolMember("array", 0x66E860)
    graphicTurn = isTurnable
    isClickable: ClassVar[BoolMember] = BoolMember("array", 0x66C150)
    useFullIscript: ClassVar[BoolMember] = BoolMember("array", 0x66D4D8)
    drawIfCloaked: ClassVar[BoolMember] = BoolMember("array", 0x667718)
    drawingFunction: ClassVar[DrawingFunctionMember] = DrawingFunctionMember(
        "array", 0x669E28
    )
    # FIXME: Add UnsupportedMember?
    # remapping: ClassVar[ArrayMember] = ArrayMember(0x669A40, Mk.BYTE)
    # Remapping table is skipped because it doesn't work in SC:R
    iscript: ClassVar[IscriptMember] = IscriptMember("array", 0x66EC48)
    # shieldsOverlay: ClassVar[ArrayMember] = ArrayMember(0x66C538, Mk.DWORD)
    # attackOverlay: ClassVar[ArrayMember] = ArrayMember(0x66B1B0, Mk.DWORD)
    # damageOverlay: ClassVar[ArrayMember] = ArrayMember(0x66A210, Mk.DWORD)
    # specialOverlay: ClassVar[ArrayMember] = ArrayMember(0x667B00, Mk.DWORD)
    # landingDustOverlay: ClassVar[ArrayMember] = ArrayMember(0x666778, Mk.DWORD)
    # liftOffDustOverlay: ClassVar[ArrayMember] = ArrayMember(0x66D8C0, Mk.DWORD)

    @ut.classproperty
    def range(self):
        return (0, 998, 1)

    @classmethod
    def cast(cls, _from: _Image):
        if isinstance(_from, ConstType) and not isinstance(_from, cls):
            raise ut.EPError(_('"{}" is not a {}').format(_from, cls.__name__))
        return super().cast(_from)

    def __init__(self, initval: _Image) -> None:
        super().__init__(EncodeImage(initval))
