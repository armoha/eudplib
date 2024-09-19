# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing_extensions import Self

from ...localize import _
from ...utils import EPError
from ..allocator.payload import _PayloadBuffer
from .eudobj import EUDObject


class Db(EUDObject):
    """Class for raw data object"""

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(self, b: bytes | int | str, /) -> None:
        super().__init__()
        if isinstance(b, str):
            b = b.encode("UTF-8")
            if 0 in b:
                raise EPError(
                    _("no nul bytes allowed in the middle of {}").format(
                        self.__class__
                    )
                )
            b += b"\0"
        self.content: bytes = bytes(b)

    def GetDataSize(self) -> int:  # noqa: N802
        return len(self.content)

    def WritePayload(self, pbuffer: _PayloadBuffer) -> None:  # noqa: N802
        pbuffer.WriteBytes(self.content)
