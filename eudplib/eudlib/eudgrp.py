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

import struct

from .. import core as c


class EUDGrp(c.EUDObject):
    """Object for GRP

    Starcraft modifies GRP in certain way before it is used ingame. This object
    emulates that modification so that SC recognizes GRP correctly.
    """

    def __init__(self, content):
        super().__init__()
        if type(content) is str:
            content = open(content, "rb").read()
        self._content = content

    def Evaluate(self):
        return c.GetObjectAddr(self) + 2

    def GetDataSize(self):
        return len(self._content) + 2

    def WritePayload(self, buf):
        buf.WriteBytes(b"\0\0")  # 2byte padding to align dwords at (*)

        # fill in grp header
        b = self._content
        fn, w, h = struct.unpack("<HHH", b[0:6])
        buf.WriteWord(fn)
        buf.WriteWord(w)
        buf.WriteWord(h)

        # fill in grp frame headers table
        selfaddr = self.Evaluate()

        for i in range(fn):
            fhoffset = 6 + 8 * i
            xoff, yoff, w, h, lto = struct.unpack("<BBBBI", b[fhoffset : fhoffset + 8])
            buf.WriteByte(xoff)
            buf.WriteByte(yoff)
            buf.WriteByte(w)
            buf.WriteByte(h)
            buf.WriteDword(lto + selfaddr)  # (*)

        buf.WriteBytes(b[6 + 8 * fn :])
