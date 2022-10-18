#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

from ..memiof import f_dwread_epd, f_dwwrite_epd
from .cpstr import GetMapStringAddr


class DBString(ut.ExprProxy):
    """Object for storing single modifiable string.

    Manipulating STR section is hard. DBString stores only one string, so that
    modifying its structure is substantially easier than modifying entire STR
    section. You can do anything you would do with normal string with DBString.
    """

    def __init__(self, content=None, *, _from=None):
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

    def GetStringMemoryAddr(self):
        """Get memory address of DBString content.

        :returns: Memory address of DBString content.
        """
        return self + 4

    @c.EUDMethod
    def Display(self):
        from .eudprint import epd2s
        from .strbuffer import GetGlobalStringBuffer

        gsb = GetGlobalStringBuffer()
        gsb.print(epd2s(ut.EPD(self) + 1))

    @c.EUDMethod
    def Play(self):
        gsb = GetGlobalStringBuffer()
        gsb.insert(0)
        gsb.append(epd2s(ut.EPD(self) + 1))
        gsb.Play()


class DBStringData(c.EUDObject):
    """Object containing DBString data"""

    def __init__(self, content):
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

    def GetDataSize(self):
        return len(self.content) + 5

    def WritePayload(self, pbuf):
        pbuf.WriteBytes(b"\x01\x00\x04\x00")
        pbuf.WriteBytes(self.content)
        pbuf.WriteByte(0)
