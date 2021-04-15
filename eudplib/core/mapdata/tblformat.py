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

from ... import utils as ut
from ...localize import _

unit_name_encoding = "cp949"


def DecodeUnitNameAs(e):
    global unit_name_encoding
    " ".encode(e)
    unit_name_encoding = e


def IgnoreColor(s):
    return bytes(filter(lambda x: not (0x01 <= x <= 0x1F or x == 0x7F), s))


def b2in(n):
    b2in_map = {2: ut.b2i2, 4: ut.b2i4}
    return b2in_map[n]


def i2bn(n):
    i2bn_map = {2: ut.i2b2, 4: ut.i2b4}
    return i2bn_map[n]


def u2bn(n):
    u2bn_map = {2: ut.u2b, 4: ut.u2utf8}
    return u2bn_map[n]


def roundup_by_4(num):
    return -((-num) // 4) * 4


class TBL:
    def __init__(self, content=None, init_chkt=None, load_entry=2, save_entry=2):
        #
        # datatb : table of strings                       : string data table
        # dataindextb : string id -> data id              : string offset table
        # stringmap : string -> representative string id
        #

        self._datatb = []
        self._stringmap = {}
        self._dataindextb = []  # String starts from #1
        self._capacity = save_entry  # Size of STR section
        self._loadentry = load_entry
        self._saveentry = save_entry
        self._emptystring = []
        self._loaded = False
        self._first_extended_string = None

        if content is not None:
            if init_chkt:
                self.LoadTBLWithChk(content, init_chkt)
            else:
                self.LoadTBL(content)

    def LoadTBL(self, content):
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

    def LoadTBLWithChk(self, content, init_chkt):
        self._datatb.clear()
        self._stringmap.clear()
        self._capacity = self._saveentry

        chkt, unitmap, locmap, swmap = init_chkt

        unix = chkt.getsection("UNIx")
        mrgn = chkt.getsection("MRGN")
        try:
            swnm = chkt.getsection("SWNM")
        except (KeyError):
            swnm = None  # Not Required
        sprp = chkt.getsection("SPRP")
        forc = chkt.getsection("FORC")

        locdict = dict()
        swnmdict = dict()
        unitdict = dict()

        # Get location names
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
                        if j in unitdict:
                            try:
                                nextstring = (
                                    nextstring.decode(unit_name_encoding)
                                ).encode("utf-8")
                            except UnicodeDecodeError:
                                pass
                        self._emptystring.append((i - 1, nextstring))
                        break
                if len(self._emptystring) == empty_len:
                    self._emptystring.append(i - 1)

            if string:
                if i in unitdict:
                    try:
                        string = (string.decode(unit_name_encoding)).encode("utf-8")
                    except UnicodeDecodeError:
                        pass
                    unitmap.AddItem(string, unitdict[i])
                    if string != IgnoreColor(string):
                        unitmap.AddItem(IgnoreColor(string), unitdict[i])
                if i in locdict:
                    locmap.AddItem(string, locdict[i])
                if i in swnmdict:
                    swmap.AddItem(string, swnmdict[i])

            if i in removed_str:
                string = b""

            self.AddString(string)
        self._loaded = True

    def AddString(self, string):
        # Starcraft: Remastered uses both utf-8 and multibyte encoding.
        try:
            string = ut.u2b(string)
        except UnicodeEncodeError:
            string = ut.u2utf8(string)
        if not isinstance(string, bytes):
            raise ut.EPError(_("Invalid type for string"))

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
                try:
                    emptystring = self._emptystring.pop(0)
                    stringindex, nextstring = emptystring
                except TypeError:
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

        ut.ep_assert(
            self._capacity < (1 << (8 * self._saveentry)), _("String table overflow")
        )

        return stringindex

    def GetString(self, index):
        if index == 0:
            return None
        else:
            try:
                dataindex = self._dataindextb[index - 1]
                return self._datatb[dataindex]
            except IndexError:
                return None

    def GetStringIndex(self, string):
        try:
            return self._stringmap[ut.u2b(string)] + 1
        except KeyError:
            try:
                return self._stringmap[ut.u2utf8(string)] + 1
            except KeyError:
                return self.AddString(string) + 1

    def SaveTBL(self):
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

    def ForceAddString(self, string):
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

        ut.ep_assert(
            self._capacity < (1 << (8 * self._saveentry)), _("String table overflow")
        )

        return stringindex
