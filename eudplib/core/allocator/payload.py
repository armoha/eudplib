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

import time
from enum import Enum
from typing import TYPE_CHECKING

from eudplib import utils as ut
from eudplib.localize import _
from eudplib.utils import RandList, ep_assert, stackobjs

from . import constexpr, pbuffer, rlocint

if TYPE_CHECKING:
    from eudplib.core.eudobj import EUDObject
_found_objects: list["EUDObject"] = []
_rootobj: "EUDObject | None" = None
_found_objects_set: set["EUDObject"] = set()
_untraversed_objects: list["EUDObject"] = []
_dynamic_objects_set: set["EUDObject"] = set()
_alloctable: dict["EUDObject", int] = {}
_payload_size: int = 0

PHASE = Enum("PHASE", ["COLLECTING", "ALLOCATING", "WRITING"])
phase: PHASE | None = None

_payload_compress: bool = False
_payload_shuffle: bool = True

# -------

_lastTime: float = 0.0
_doLog: bool = False


def setPayloadLoggerMode(mode: bool) -> None:
    global _doLog
    _doLog = mode


def lprint(text, flush: bool = False):
    global _lastTime, _doLog
    if not _doLog:
        return

    currentTime = time.time()
    if flush or (currentTime - _lastTime) >= 0.5:
        _lastTime = currentTime
        print(text, end="\n" if flush else "\r")


def CompressPayload(mode: bool) -> None:
    """Set payload compression mode.

    :param mode: If true, enable object stacking (compression). If false,
    disable it.
    """
    global _payload_compress
    ut.ep_assert(mode in (True, False), _("Invalid type") + f": {mode}")
    _payload_compress = True if mode else False


def ShufflePayload(mode: bool) -> None:
    """Set payload shuffle mode.

    :param mode: If true, enable object shuffling (compression). If false,
    disable it.
    """
    global _payload_shuffle
    ut.ep_assert(mode in (True, False), _("Invalid type") + f": {mode}")
    _payload_shuffle = True if mode else False


class ObjCollector:

    """
    Object having PayloadBuffer-like interfaces. Collects all objects by
    calling RegisterObject() for every related objects.
    """

    def __init__(self):
        pass

    def StartWrite(self) -> None:
        pass

    def EndWrite(self):
        pass

    def WriteByte(self, number) -> None:
        pass

    def WriteWord(self, number) -> None:
        pass

    def WriteDword(self, number) -> None:
        if type(number) is not int:
            constexpr.Evaluate(number)

    def WritePack(self, structformat, arglist) -> None:
        for arg in arglist:
            if type(arg) is not int:
                constexpr.Evaluate(arg)

    def WriteBytes(self, b) -> None:
        pass

    def WriteSpace(self, spacesize) -> None:
        pass


def CollectObjects(root) -> None:
    global phase
    global _rootobj
    global _found_objects
    global _found_objects_set
    global _dynamic_objects_set
    global _untraversed_objects

    lprint(_("[Stage 1/3] CollectObjects"), flush=True)

    phase = PHASE.COLLECTING

    objc = ObjCollector()
    _rootobj = None
    _found_objects_set = set()
    _dynamic_objects_set = set()
    _untraversed_objects = []

    # Evaluate root to register root object.
    # root may not have WritePayload() method e.g: Forward()
    constexpr.Evaluate(root)

    while _untraversed_objects:
        while _untraversed_objects:
            lprint(
                _(" - Collected {} / {} objects").format(
                    len(_found_objects_set),
                    len(_found_objects_set) + len(_untraversed_objects),
                )
            )

            obj = _untraversed_objects.pop()

            objc.StartWrite()
            obj.CollectDependency(objc)
            objc.EndWrite()

        # Check for new objects
        for obj in _dynamic_objects_set:
            objc.StartWrite()
            obj.CollectDependency(objc)
            objc.EndWrite()

    if len(_found_objects_set) == 0:
        raise ut.EPError(_("No object collected"))

    if _payload_shuffle:
        # Shuffle objects -> Randomize(?) addresses
        if _rootobj:
            _found_objects_set.remove(_rootobj)
        _found_objects = [_rootobj] + RandList(_found_objects_set)

    # cleanup
    _found_objects_set.clear()
    phase = None

    # Final
    lprint(
        _(" - Collected {} / {} objects").format(len(_found_objects), len(_found_objects)),
        flush=True,
    )
    if not _payload_shuffle:
        lprint(_("ShufflePayload has been turned off."), flush=True)


# -------


class ObjAllocator:

    """
    Object having PayloadBuffer-like interfaces. Collects all objects by
    calling RegisterObject() for every related objects.
    """

    def __init__(self):
        self._sizes = {}

    def StartWrite(self) -> None:
        self._suboccupmap: int = 0
        self._suboccupidx: int = 0
        self._occupmap: list[int] = []

    def _Occup0(self) -> None:
        self._suboccupidx += 1
        if self._suboccupidx == 4:
            self._occupmap.append(self._suboccupmap)
            self._suboccupidx = 0
            self._suboccupmap = 0

    def _Occup1(self) -> None:
        self._suboccupmap = 1
        self._suboccupidx += 1
        if self._suboccupidx == 4:
            self._occupmap.append(self._suboccupmap)
            self._suboccupidx = 0
            self._suboccupmap = 0

    def EndWrite(self):
        if self._suboccupidx:
            self._occupmap.append(self._suboccupmap)
            self._suboccupidx = 0
        return self._occupmap

    def WriteByte(self, number) -> None:
        if number is None:
            self._Occup0()
        else:
            self._Occup1()

    def WriteWord(self, number) -> None:
        if number is None:
            self._Occup0()
            self._Occup0()
        else:
            self._Occup1()
            self._Occup1()

    def WriteDword(self, number) -> None:
        self._occupmap.append(1)

    def WritePack(self, structformat, arglist) -> None:
        if structformat not in self._sizes:
            ssize = 0
            sizedict = {"B": 1, "H": 2, "I": 4}
            for b in structformat:
                ssize += sizedict[b]
            self._sizes[structformat] = ssize

        ssize = self._sizes[structformat]

        # Add occupation index
        self._occupmap.extend([1] * (ssize >> 2))
        ssize &= 3
        for i in range(ssize):
            self._Occup1()

    def WriteBytes(self, b) -> None:
        ssize = len(b)
        self._occupmap.extend([1] * (ssize >> 2))
        for i in range(ssize & 3):
            self._Occup1()

    def WriteSpace(self, ssize) -> None:
        self._suboccupidx += ssize
        if self._suboccupidx >= 4:
            self._occupmap.append(self._suboccupmap)
            self._suboccupidx -= 4
            remaining0 = self._suboccupidx // 4
            self._occupmap.extend([0] * remaining0)
            self._suboccupidx %= 4
            self._suboccupmap = 0


def AllocObjects():
    global phase
    global _alloctable
    global _payload_size

    phase = PHASE.ALLOCATING
    objn = len(_found_objects)

    lprint(_("[Stage 2/3] AllocObjects"), flush=True)

    # Quick and less space-efficient approach
    if not _payload_compress:
        lallocaddr = 0
        for i, obj in enumerate(_found_objects):
            objsize = obj.GetDataSize()
            allocsize = (objsize + 3) & ~3
            _alloctable[obj] = lallocaddr
            lallocaddr += allocsize

            lprint(_(" - Allocated {} / {} objects").format(i + 1, objn))
        _payload_size = lallocaddr

        lprint(_(" - Allocated {} / {} objects").format(objn, objn), flush=True)
        phase = None
        return

    obja = ObjAllocator()

    _alloctable = {}
    dwoccupmap_dict = {}

    # Get occupation map for all objects
    for i, obj in enumerate(_found_objects):
        obja.StartWrite()
        obj.WritePayload(obja)
        dwoccupmap = obja.EndWrite()
        dwoccupmap_dict[obj] = dwoccupmap
        if len(dwoccupmap) != (obj.GetDataSize() + 3) >> 2:

            raise ut.EPError(
                _("Occupation map length ({}) & Object size mismatch for object ({})").format(
                    len(dwoccupmap), (obj.GetDataSize() + 3) >> 2
                )
            )
        lprint(_(" - Preprocessed {} / {} objects").format(i + 1, objn))

    lprint(_(" - Preprocessed {} / {} objects").format(objn, objn), flush=True)

    lprint(_(" - Allocating objects.."), flush=True)
    stackobjs.StackObjects(_found_objects, dwoccupmap_dict, _alloctable)

    # Get payload length
    _payload_size = max(map(lambda obj: _alloctable[obj] + obj.GetDataSize(), _found_objects))

    phase = None


# -------


def ConstructPayload():
    global phase

    phase = PHASE.WRITING
    lprint(_("[Stage 3/3] ConstructPayload"), flush=True)
    objn = len(_found_objects)

    pbuf = pbuffer.PayloadBuffer(_payload_size)

    for i, obj in enumerate(_found_objects):
        objaddr, objsize = _alloctable[obj], obj.GetDataSize()

        pbuf.StartWrite(objaddr)
        obj.WritePayload(pbuf)
        written_bytes = pbuf.EndWrite()
        ut.ep_assert(
            written_bytes == objsize,
            _("obj.GetDataSize()({}) != Real payload size({}) for object {}").format(
                objsize, written_bytes, obj
            ),
        )

        lprint(_(" - Written {} / {} objects").format(i + 1, objn))

    lprint(_(" - Written {} / {} objects").format(objn, objn), flush=True)
    phase = None
    return pbuf.CreatePayload()


_on_create_payload_callbacks = []


def RegisterCreatePayloadCallback(f):
    _on_create_payload_callbacks.append(f)


def CreatePayload(root):
    # Call callbacks
    for f in _on_create_payload_callbacks:
        f()
    CollectObjects(root)
    AllocObjects()
    return ConstructPayload()


defri = rlocint.RlocInt(0, 4)


def GetObjectAddr(obj):
    global _alloctable
    global _found_objects
    global _found_objects_set
    global _untraversed_objects
    global _dynamic_objects_set
    global _rootobj

    if phase is PHASE.COLLECTING:
        if obj not in _found_objects_set:
            _untraversed_objects.append(obj)
            _found_objects.append(obj)
            _found_objects_set.add(obj)
            if obj.DynamicConstructed():
                _dynamic_objects_set.add(obj)
            if not _rootobj:
                _rootobj = obj

        return defri

    elif phase is PHASE.ALLOCATING:
        return defri

    elif phase is PHASE.WRITING:
        # ep_assert(_alloctable[obj] & 3 == 0)
        return rlocint.RlocInt_C(_alloctable[obj], 4)
