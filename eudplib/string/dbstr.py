# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing_extensions import Self

from .. import core as c
from .. import utils as ut
from ..ctrlstru import DoActions
from .strcommon import temp_string_id


class DBString(ut.ExprProxy):
    """Object for storing single modifiable string.

    Manipulating STR section is hard. DBString stores only one string, so that
    modifying its structure is substantially easier than modifying entire STR
    section. You can do anything you would do with normal string with DBString.
    """

    def __init__(self, content=None, *, _from=None) -> None:
        """Constructor for DBString

        :param content: Initial DBString content / capacity. Capacity of
            DBString is determined by size of this. If content is integer, then
            initial capacity and content of DBString will be set to
            content(int) and empty string.

        :type content: str, bytes, int
        """
        if _from is None:
            super().__init__(DBStringData(content))
        elif type(_from) in (str, bytes):
            super().__init__(DBStringData(_from))
        else:
            super().__init__(_from)

    def GetStringMemoryAddr(self):  # noqa: N802
        """Get memory address of DBString content.

        :returns: Memory address of DBString content.
        """
        return self

    def Display(self):  # noqa: N802
        strid = temp_string_id()
        DoActions(
            c.SetMemory(0x191943C8 + 4 * strid, c.SetTo, self - 0x191943C8),
            c.DisplayText(strid),
        )

    def Play(self):  # noqa: N802
        strid = temp_string_id()
        DoActions(
            c.SetMemory(0x191943C8 + 4 * strid, c.SetTo, self - 0x191943C8),
            c.PlayWAV(strid),
        )


class DBStringData(c.EUDObject):
    """Object containing DBString data"""

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(self, content) -> None:
        """Constructor for DBString

        :param content: Initial DBString content / capacity. Capacity of
            DBString is determined by size of this. If content is integer, then
            initial capacity and content of DBString will be set to
            content(int) and empty string.

        :type content: str, bytes, int
        """
        super().__init__()
        if isinstance(content, int):
            self.content = bytes(content)
        else:
            self.content = ut.u2utf8(content)

    def GetDataSize(self):  # noqa: N802
        return len(self.content) + 1

    def WritePayload(self, pbuf):  # noqa: N802
        pbuf.WriteBytes(self.content)
        pbuf.WriteByte(0)
