#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
"""
String table manager. Internally used in eudplib.
"""

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Literal

from ... import utils as ut
from ...localize import _
from .chktok import CHK

if TYPE_CHECKING:
    from .stringmap import StringIdMap

unit_name_encoding: str | None = None


def DecodeUnitNameAs(e: str) -> None:  # noqa: N802
    global unit_name_encoding
    "".encode(e)  # check if e is valid encoding
    unit_name_encoding = e


def _ignore_color(s: bytes) -> bytes | None:
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


def _b2in(n: int) -> Callable[[Sequence[int], int], int]:
    b2in_map = {2: ut.b2i2, 4: ut.b2i4}
    return b2in_map[n]


def _i2bn(n: int) -> Callable[[int], bytes]:
    i2bn_map = {2: ut.i2b2, 4: ut.i2b4}
    return i2bn_map[n]


def _roundup_by_4(num: int) -> int:
    return -((-num) // 4) * 4


class TBL:
    def __init__(
        self,
        content: bytes | None = None,
        init_chkt: "tuple[CHK, StringIdMap, StringIdMap, StringIdMap] | None" = None,
        *,
        load_entry: Literal[2, 4] = 2,
        save_entry: Literal[2, 4] = 4,
    ) -> None:
        self._loadentry: Literal[2, 4] = load_entry
        self._saveentry: Literal[2, 4] = save_entry

        # datatb : table of strings                       : string data table
        # dataindextb : string id -> data id              : string offset table
        # stringmap : string -> representative string id
        self._datatb: list[bytes] = []
        self._stringmap: dict[bytes, int] = {}
        self._dataindextb: list[int] = []  # String starts from #1
        self._capacity: int = save_entry  # Size of STR section
        self._emptystring: list[tuple[int, bytes] | int] = []
        self._loaded: bool = False
        self._first_extended_string: bytes | None = None

        self._finalized: bool = False
        self._tbldata: bytes = b""
        self._stroffset: list[int] = []

        if content is not None:
            if init_chkt:
                self.load_tbl_with_chk(content, init_chkt)
            else:
                self.load_tbl(content)

    def load_tbl(self, content: bytes) -> None:
        # ut.ep_assert(not self._loaded, "String data are already loaded")
        self._datatb.clear()
        self._stringmap.clear()
        self._dataindextb.clear()
        self._emptystring.clear()
        self._first_extended_string = None
        self._capacity = self._saveentry

        size = self._loadentry
        b2i = _b2in(size)
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

    def load_tbl_with_chk(
        self,
        content: bytes,
        init_chkt: "tuple[CHK, StringIdMap, StringIdMap, StringIdMap]",
    ) -> None:
        # ut.ep_assert(not self._loaded, "String data are already loaded")
        self._datatb.clear()
        self._stringmap.clear()
        self._dataindextb.clear()
        self._emptystring.clear()
        self._first_extended_string = None
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
        b2i = _b2in(size)
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
                    continue
                else:
                    # no null terminator
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
                    if unit_name_encoding:
                        try:
                            string = (string.decode(unit_name_encoding)).encode(
                                "utf-8"
                            )
                        except UnicodeDecodeError:
                            pass
                    unitmap.add_item(string, unitdict[i])
                    color_erased = _ignore_color(string)
                    if color_erased:
                        unitmap.add_item(color_erased, unitdict[i])
                if i in locdict:
                    locmap.add_item(string, locdict[i])
                if i in swnmdict:
                    swmap.add_item(string, swnmdict[i])

            if i in removed_str:
                string = b""

            self.AddString(string)
        self._loaded = True

    def AddString(self, string: str | bytes) -> int:  # noqa: N802
        ut.ep_assert(
            not self._finalized, _("Can't add new string after finalization")
        )
        # Starcraft: Remastered uses both utf-8 and multibyte encoding.
        if isinstance(string, str):
            try:
                string = ut.u2utf8(string)
            except UnicodeEncodeError:
                string = ut.u2b(string)
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
                self._capacity += _roundup_by_4(len(string) + 1)
            else:
                if self._first_extended_string is None:
                    self._first_extended_string = string
                dataindex = len(self._datatb)
                self._datatb.append(string)
                self._dataindextb.append(dataindex)
                # string + b'\0' + string offset
                self._capacity += _roundup_by_4(len(string) + 1) + self._saveentry
            self._stringmap[string] = stringindex

        ut.ep_assert(
            self._capacity < (1 << (8 * self._saveentry)),
            _("String table overflow"),
        )
        ut.ep_assert(0 <= stringindex < 65535, _("String count exceeded"))

        return stringindex

    def GetString(self, index: int) -> bytes | None:  # noqa: N802
        if index == 0:
            return None
        else:
            try:
                dataindex = self._dataindextb[index - 1]
                return self._datatb[dataindex]
            except IndexError:
                return None

    def GetStringIndex(self, string: str | bytes) -> int:  # noqa: N802
        try:
            return self._stringmap[ut.u2b(string)] + 1
        except KeyError:
            try:
                return self._stringmap[ut.u2utf8(string)] + 1
            except KeyError:
                return self.AddString(string) + 1

    def save_tbl(self) -> bytes:
        if self._finalized:
            return self._tbldata

        # calculate offset of each string
        outbytes = []
        self._stroffset.clear()
        size = self._saveentry
        outindex = _roundup_by_4(size * len(self._dataindextb) + size)

        for s in self._datatb:
            self._stroffset.append(outindex)
            outindex += _roundup_by_4(len(s) + 1)
        i2b = _i2bn(size)

        # String count
        outbytes.append(i2b(len(self._dataindextb)))

        # String offsets
        for dataidx in self._dataindextb:
            outbytes.append(i2b(self._stroffset[dataidx]))

        tablesize = size * (len(self._dataindextb) + 1)
        for _n in range(_roundup_by_4(tablesize) - tablesize):
            outbytes.append(b"\0")

        # String data
        for s in self._datatb:
            outbytes.append(s)
            for _n in range(_roundup_by_4(len(s) + 1) - len(s)):
                outbytes.append(b"\0")

        self._tbldata = b"".join(outbytes)
        return self._tbldata

    def finalize(self) -> tuple[bytes, list[int]]:
        self.save_tbl()
        self._finalized = True
        return self._tbldata, self._stroffset

    def ForceAddString(self, string: str | bytes) -> int:  # noqa: N802
        ut.ep_assert(
            not self._finalized, _("Can't add new string after finalization")
        )
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
        self._capacity += _roundup_by_4(len(string) + 1) + self._saveentry

        ut.ep_assert(
            self._capacity < (1 << (8 * self._saveentry)),
            _("String table overflow"),
        )
        ut.ep_assert(0 <= stringindex < 65535, _("String count exceeded"))

        return stringindex
