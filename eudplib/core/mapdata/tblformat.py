#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
String table manager. Internally used in eudplib.

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

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Literal

from ... import utils as ut
from ...localize import _
from .chktok import CHK

if TYPE_CHECKING:
    from .stringmap import StringIdMap

unit_name_encoding: str | None = None


def DecodeUnitNameAs(e: str) -> None:
    global unit_name_encoding
    "".encode(e)  # check if e is valid encoding
    unit_name_encoding = e


def IgnoreColor(s: bytes) -> bytes | None:
    has_color = False
    ret = []
    for x in s:
        if 0x01 <= x <= 0x1F or x == 0x7F:
            has_color = True
        else:
            ret.append(x)
    if has_color:
        return bytes(ret)
    else:
        return None


def b2in(n: int) -> "Callable[[Sequence[int], int], int]":
    b2in_map = {2: ut.b2i2, 4: ut.b2i4}
    return b2in_map[n]


def i2bn(n: int) -> "Callable[[int], bytes]":
    i2bn_map = {2: ut.i2b2, 4: ut.i2b4}
    return i2bn_map[n]


def u2bn(n: int) -> "Callable[[str | bytes], bytes]":
    u2bn_map = {2: ut.u2b, 4: ut.u2utf8}
    return u2bn_map[n]


def roundup_by_4(num: int) -> int:
    return -((-num) // 4) * 4


class TBL:
    def __init__(
        self,
        content: bytes | None = None,
        init_chkt: "tuple[CHK, StringIdMap, StringIdMap, StringIdMap] | None" = None,
        load_entry: "Literal[2, 4]" = 2,
        save_entry: "Literal[2, 4]" = 4,
    ) -> None:
        #
        # datatb : table of strings                       : string data table
        # dataindextb : string id -> data id              : string offset table
        # stringmap : string -> representative string id
        #

        self._datatb: "list[bytes]" = []
        self._stringmap: "dict[bytes, int]" = {}
        self._dataindextb: "list[int]" = []  # String starts from #1
        self._capacity: int = save_entry  # Size of STR section
        self._loadentry: "Literal[2, 4]" = load_entry
        self._saveentry: "Literal[2, 4]" = save_entry
        self._emptystring: "list[tuple[int, bytes] | int]" = []
        self._loaded: bool = False
        self._first_extended_string: bytes | None = None

        if content is not None:
            if init_chkt:
                self.LoadTBLWithChk(content, init_chkt)
            else:
                self.LoadTBL(content)

    def LoadTBL(self, content: bytes) -> None:
        self._datatb.clear()
        self._stringmap.clear()
        self._capacity = self._saveentry

        size = self._loadentry
        b2i = b2in(size)
        stringcount = b2i(content, 0)

        for i in range(stringcount):
            i += 1
            stringoffset = b2i(content, i * size)
            send = stringoffset
            while content[send] != 0:
                send += 1

            string = content[stringoffset:send]
            if string == b"":
                empty_len = len(self._emptystring)
                for j in range(i, stringcount):
                    j += 1
                    nextoffset = b2i(content, j * size)
                    nextend = nextoffset
                    while content[nextend] != 0:
                        nextend += 1
                    nextstring = content[nextoffset:nextend]
                    if nextstring != b"":
                        self._emptystring.append((i - 1, nextstring))
                        break
                if len(self._emptystring) == empty_len:
                    self._emptystring.append(i - 1)
            self.AddString(string)
        self._loaded = True

    def LoadTBLWithChk(
        self, content: bytes, init_chkt: "tuple[CHK, StringIdMap, StringIdMap, StringIdMap]"
    ) -> None:
        self._datatb.clear()
        self._stringmap.clear()
        self._capacity = self._saveentry

        chkt, unitmap, locmap, swmap = init_chkt

        unix = chkt.getsection("UNIx")
        try:
            swnm = chkt.getsection("SWNM")
        except KeyError:
            swnm = None
        sprp = chkt.getsection("SPRP")
        forc = chkt.getsection("FORC")

        locdict = dict()
        swnmdict = dict()
        unitdict = dict()

        # Get location names
        try:
            mrgn = chkt.getsection("MRGN")
        except KeyError:
            pass  # Not Required for Melee
        else:
            if mrgn:
                locn = len(mrgn) // 20
                for i in range(locn):
                    locstrid = ut.b2i2(mrgn, 20 * i + 16)
                    if locstrid:
                        locdict[locstrid] = i

        # Get switch names
        if swnm:
            for i in range(256):
                swstrid = ut.b2i4(swnm, 4 * i)
                if swstrid:
                    swnmdict[swstrid] = i

        # Get unit names
        if unix:
            for i in range(228):
                unitstrid = ut.b2i2(unix, 3192 + i * 2)
                if unitstrid:
                    unitdict[unitstrid] = i

        reserved_str = set(unitdict.keys())

        if sprp:
            for i in range(2):
                mapstrid = ut.b2i2(sprp, i * 2)
                if mapstrid:
                    reserved_str.add(mapstrid)

        if forc:
            for i in range(4):
                forcstrid = ut.b2i2(forc, 8 + i * 2)
                if forcstrid:
                    reserved_str.add(forcstrid)

        size = self._loadentry
        b2i = b2in(size)
        removed_str = set(locdict.keys()).union(swnmdict.keys()) - reserved_str
        stringcount = b2i(content, 0)

        for i in range(stringcount):
            i += 1
            stringoffset = b2i(content, i * size)
            send = stringoffset
            try:
                while content[send] != 0:
                    send += 1
            except IndexError:
                if stringoffset == send:
                    # invalid string offset
                    # print("String[{}] has invalid string offset: {:X}".format(i, stringoffset))
                    continue
                else:
                    # no null terminator
                    # print("String[{}] has no null terminator: {}".format(i, content[stringoffset:send].decode("CP949")))
                    pass

            string = content[stringoffset:send]
            if string == b"" or i in removed_str:
                empty_len = len(self._emptystring)
                for j in range(i, stringcount):
                    j += 1
                    if j in removed_str:
                        continue
                    nextoffset = b2i(content, j * size)
                    nextend = nextoffset
                    while content[nextend] != 0:
                        nextend += 1
                    nextstring = content[nextoffset:nextend]
                    if nextstring != b"":
                        if j in unitdict and unit_name_encoding:
                            try:
                                nextstring = (nextstring.decode(unit_name_encoding)).encode(
                                    "utf-8"
                                )
                            except UnicodeDecodeError:
                                pass
                        self._emptystring.append((i - 1, nextstring))
                        break
                if len(self._emptystring) == empty_len:
                    self._emptystring.append(i - 1)

            if string:
                if i in unitdict:
                    if unit_name_encoding:
                        try:
                            string = (string.decode(unit_name_encoding)).encode("utf-8")
                        except UnicodeDecodeError:
                            pass
                    unitmap.AddItem(string, unitdict[i])
                    color_erased = IgnoreColor(string)
                    if color_erased:
                        unitmap.AddItem(color_erased, unitdict[i])
                if i in locdict:
                    locmap.AddItem(string, locdict[i])
                if i in swnmdict:
                    swmap.AddItem(string, swnmdict[i])

            if i in removed_str:
                string = b""

            self.AddString(string)
        self._loaded = True

    def AddString(self, string: str | bytes) -> int:
        # Starcraft: Remastered uses both utf-8 and multibyte encoding.
        try:
            string = ut.u2b(string)
        except UnicodeEncodeError:
            string = ut.u2utf8(string)
        if not isinstance(string, bytes):
            raise ut.EPError(_("Invalid type for string") + f": {string}")

        stringindex = len(self._dataindextb)

        # If duplicate text exist -> just proxy it
        try:
            repr_stringid = self._stringmap[string]
            dataindex = self._dataindextb[repr_stringid]
            self._dataindextb.append(dataindex)
            self._capacity += self._saveentry  # just string offset

        # Else -> Create new entry
        except KeyError:
            if self._emptystring and self._loaded and self._first_extended_string:
                emptystring = self._emptystring.pop(0)
                if isinstance(emptystring, tuple):
                    stringindex, nextstring = emptystring
                else:
                    stringindex = emptystring
                    nextstring = self._first_extended_string
                dataindex = self._datatb.index(nextstring)
                self._datatb.insert(dataindex, string)
                for i, v in enumerate(self._dataindextb):
                    if v >= dataindex:
                        self._dataindextb[i] += 1
                self._dataindextb[stringindex] = dataindex
                # string + b'\0'
                self._capacity += roundup_by_4(len(string) + 1)
            else:
                if self._first_extended_string is None:
                    self._first_extended_string = string
                dataindex = len(self._datatb)
                self._datatb.append(string)
                self._dataindextb.append(dataindex)
                # string + b'\0' + string offset
                self._capacity += roundup_by_4(len(string) + 1) + self._saveentry
            self._stringmap[string] = stringindex

        ut.ep_assert(self._capacity < (1 << (8 * self._saveentry)), _("String table overflow"))

        return stringindex

    def GetString(self, index: int) -> bytes | None:
        if index == 0:
            return None
        else:
            try:
                dataindex = self._dataindextb[index - 1]
                return self._datatb[dataindex]
            except IndexError:
                return None

    def GetStringIndex(self, string: str | bytes) -> int:
        try:
            return self._stringmap[ut.u2b(string)] + 1
        except KeyError:
            try:
                return self._stringmap[ut.u2utf8(string)] + 1
            except KeyError:
                return self.AddString(string) + 1

    def SaveTBL(self) -> bytes:
        outbytes = []

        # calculate offset of each string
        stroffset = []
        size = self._saveentry
        outindex = roundup_by_4(size * len(self._dataindextb) + size)

        for s in self._datatb:
            stroffset.append(outindex)
            outindex += roundup_by_4(len(s) + 1)
        i2b = i2bn(size)

        # String count
        outbytes.append(i2b(len(self._dataindextb)))

        # String offsets
        for dataidx in self._dataindextb:
            outbytes.append(i2b(stroffset[dataidx]))

        tablesize = size * (len(self._dataindextb) + 1)
        for _ in range(roundup_by_4(tablesize) - tablesize):
            outbytes.append(b"\0")

        # String data
        for s in self._datatb:
            outbytes.append(s)
            for _ in range(roundup_by_4(len(s) + 1) - len(s)):
                outbytes.append(b"\0")

        return b"".join(outbytes)

    def ForceAddString(self, string: str | bytes) -> int:
        string = ut.u2b(string)  # Starcraft uses multibyte encoding.
        if not isinstance(string, bytes):
            raise ut.EPError(_("Invalid type for string"))

        stringindex = len(self._dataindextb)

        # Always -> Create new entry
        dataindex = len(self._datatb)
        # self._stringmap[string] = stringindex
        self._datatb.append(string)
        self._dataindextb.append(dataindex)
        # string + b'\0' + string offset
        self._capacity += roundup_by_4(len(string) + 1) + self._saveentry

        ut.ep_assert(self._capacity < (1 << (8 * self._saveentry)), _("String table overflow"))

        return stringindex
