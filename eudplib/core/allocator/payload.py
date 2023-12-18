#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import time
from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, TypeAlias

from eudplib.localize import _
from eudplib.utils import EPError, _rand_lst, ep_assert
from eudplib.bindings._rust import allocator

from .constexpr import Evaluable, Evaluate, Forward
from .pbuffer import Payload, PayloadBuffer
from .rlocint import RlocInt, RlocInt_C

if TYPE_CHECKING:
    from ..eudobj import EUDObject

_found_objects_dict: "dict[EUDObject, int]" = {}
_untraversed_objects: "list[EUDObject]" = []
_dynamic_objects_set: "set[EUDObject]" = set()
_alloctable: "list[int]" = []
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


def lprint(text: str, flush: bool = False):
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
    ep_assert(mode in (True, False), _("Invalid type") + f": {mode}")
    _payload_compress = True if mode else False


def ShufflePayload(mode: bool) -> None:
    """Set payload shuffle mode.

    :param mode: If true, enable object shuffling (compression). If false,
    disable it.
    """
    global _payload_shuffle
    ep_assert(mode in (True, False), _("Invalid type") + f": {mode}")
    _payload_shuffle = True if mode else False


class ObjCollector:
    """
    Object having PayloadBuffer-like interfaces. Collects all objects by
    calling RegisterObject() for every related objects.
    """

    def __init__(self) -> None:
        pass

    def StartWrite(self) -> None:
        pass

    def EndWrite(self) -> None:
        pass

    def WriteByte(self, number: int) -> None:
        pass

    def WriteWord(self, number: int) -> None:
        pass

    def WriteDword(self, obj: Evaluable) -> None:
        if not isinstance(obj, int):
            Evaluate(obj)

    def WritePack(self, structformat: str, arglist: list[Evaluable]) -> None:
        for arg in arglist:
            if not isinstance(arg, int):
                Evaluate(arg)

    def WriteBytes(self, b: bytes) -> None:
        pass

    def WriteSpace(self, spacesize: int) -> None:
        pass


def CollectObjects(root: "EUDObject | Forward") -> None:
    global phase
    global _found_objects_dict
    global _dynamic_objects_set
    global _untraversed_objects

    lprint(_("[Stage 1/3] CollectObjects"), flush=True)

    phase = PHASE.COLLECTING

    objc = ObjCollector()
    _found_objects_dict = {}
    _dynamic_objects_set = set()
    _untraversed_objects = []

    # Evaluate root to register root object.
    # root may not have WritePayload() method e.g: Forward()
    Evaluate(root)

    while _untraversed_objects:
        while _untraversed_objects:
            lprint(
                _(" - Collected {} / {} objects").format(
                    len(_found_objects_dict),
                    len(_found_objects_dict) + len(_untraversed_objects),
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

    if len(_found_objects_dict) == 0:
        raise EPError(_("No object collected"))

    if _payload_shuffle:
        # Shuffle objects -> Randomize(?) addresses
        iterobj = iter(_found_objects_dict)
        rootobj = next(iterobj)
        found_objects = _rand_lst(iterobj)
        found_objects.append(rootobj)
        _found_objects_dict = {obj: i for i, obj in enumerate(reversed(found_objects))}

    # cleanup
    phase = None

    # Final
    lprint(
        _(" - Collected {} / {} objects").format(
            len(_found_objects_dict), len(_found_objects_dict)
        ),
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

    def __init__(self) -> None:
        self._sizes: dict[str, int] = {}

    def StartWrite(self) -> None:
        self._suboccupmap: bool = False
        self._suboccupidx: int = 0
        self._occupmap: list[bool] = []

    def _Occup0(self) -> None:
        self._suboccupidx += 1
        if self._suboccupidx == 4:
            self._occupmap.append(self._suboccupmap)
            self._suboccupidx = 0
            self._suboccupmap = False

    def _Occup1(self) -> None:
        self._suboccupmap = True
        self._suboccupidx += 1
        if self._suboccupidx == 4:
            self._occupmap.append(self._suboccupmap)
            self._suboccupidx = 0
            self._suboccupmap = False

    def EndWrite(self) -> list[bool]:
        if self._suboccupidx:
            self._occupmap.append(self._suboccupmap)
            self._suboccupidx = 0
        return self._occupmap

    def WriteByte(self, number: int) -> None:
        if number is None:
            self._Occup0()
        else:
            self._Occup1()

    def WriteWord(self, number: int) -> None:
        if number is None:
            self._Occup0()
            self._Occup0()
        else:
            self._Occup1()
            self._Occup1()

    def WriteDword(self, obj: Evaluable) -> None:
        self._occupmap.append(True)

    def WritePack(self, structformat: str, arglist: list[Evaluable]) -> None:
        if structformat not in self._sizes:
            ssize = 0
            sizedict = {"B": 1, "H": 2, "I": 4}
            for b in structformat:
                ssize += sizedict[b]
            self._sizes[structformat] = ssize

        ssize = self._sizes[structformat]

        # Add occupation index
        self._occupmap.extend([True] * (ssize >> 2))
        ssize &= 3
        for i in range(ssize):
            self._Occup1()

    def WriteBytes(self, b: bytes) -> None:
        ssize = len(b)
        self._occupmap.extend([True] * (ssize >> 2))
        for i in range(ssize & 3):
            self._Occup1()

    def WriteSpace(self, ssize: int) -> None:
        self._suboccupidx += ssize
        if self._suboccupidx >= 4:
            self._occupmap.append(self._suboccupmap)
            self._suboccupidx -= 4
            remaining0 = self._suboccupidx // 4
            self._occupmap.extend([False] * remaining0)
            self._suboccupidx %= 4
            self._suboccupmap = False


def AllocObjects() -> None:
    global phase
    global _alloctable
    global _payload_size

    phase = PHASE.ALLOCATING
    objn = len(_found_objects_dict)

    lprint(_("[Stage 2/3] AllocObjects"), flush=True)

    # Quick and less space-efficient approach
    if not _payload_compress:
        lallocaddr = 0
        for i, obj in enumerate(_found_objects_dict):
            objsize = obj.GetDataSize()
            allocsize = (objsize + 3) & ~3
            lallocaddr += allocsize

            lprint(_(" - Allocated {} / {} objects").format(i + 1, objn))
        _payload_size = lallocaddr

        lprint(_(" - Allocated {} / {} objects").format(objn, objn), flush=True)
        phase = None
        return

    obja = ObjAllocator()

    _alloctable = []
    dwoccupmap_list: list[list[bool]] = []

    # Get occupation map for all objects
    for i, obj in enumerate(_found_objects_dict):
        obja.StartWrite()
        obj.WritePayload(obja)
        dwoccupmap = obja.EndWrite()
        dwoccupmap_list.append(dwoccupmap)
        if len(dwoccupmap) != (obj.GetDataSize() + 3) >> 2:
            e = _("Occupation map length ({}) & Object size mismatch for object ({})")  # noqa: E501
            e = e.format(len(dwoccupmap), (obj.GetDataSize() + 3) >> 2)
            raise EPError(e)
        lprint(_(" - Preprocessed {} / {} objects").format(i + 1, objn))

    lprint(_(" - Preprocessed {} / {} objects").format(objn, objn), flush=True)

    lprint(_(" - Allocating objects.."), flush=True)
    _alloctable, _payload_size = allocator.stack_objects(dwoccupmap_list)

    phase = None


# -------


def ConstructPayload() -> Payload:
    global phase

    phase = PHASE.WRITING
    lprint(_("[Stage 3/3] ConstructPayload"), flush=True)
    objn = len(_found_objects_dict)

    pbuf = PayloadBuffer(_payload_size)

    for i, obj in enumerate(_found_objects_dict):
        objaddr, objsize = _alloctable[i], obj.GetDataSize()

        pbuf.StartWrite(objaddr)
        obj.WritePayload(pbuf)
        written_bytes = pbuf.EndWrite()
        ep_assert(
            written_bytes == objsize,
            _("obj.GetDataSize()({}) != Real payload size({}) for object {}").format(
                objsize, written_bytes, obj
            ),
        )

        lprint(_(" - Written {} / {} objects").format(i + 1, objn))

    lprint(_(" - Written {} / {} objects").format(objn, objn), flush=True)
    phase = None
    return pbuf.CreatePayload()


_on_create_payload_callbacks: list[Callable] = []
_on_alloc_objects_callbacks: list[Callable] = []


def RegisterCreatePayloadCallback(f: Callable) -> None:
    _on_create_payload_callbacks.append(f)


def _RegisterAllocObjectsCallback(f: Callable) -> None:
    _on_alloc_objects_callbacks.append(f)


def CreatePayload(root: "EUDObject | Forward") -> Payload:
    # Call callbacks
    for f in _on_create_payload_callbacks:
        f()
    CollectObjects(root)
    for f in _on_alloc_objects_callbacks:
        f()
    AllocObjects()
    return ConstructPayload()


_PayloadBuffer: TypeAlias = ObjCollector | ObjAllocator | PayloadBuffer
defri: RlocInt_C = RlocInt(0, 4)


def GetObjectAddr(obj: "EUDObject") -> RlocInt_C:
    global _alloctable
    global _found_objects_dict
    global _untraversed_objects
    global _dynamic_objects_set

    if phase is PHASE.COLLECTING:
        if obj not in _found_objects_dict:
            _untraversed_objects.append(obj)
            _found_objects_dict[obj] = len(_found_objects_dict)
            if obj.DynamicConstructed():
                _dynamic_objects_set.add(obj)

        return defri

    elif phase is PHASE.ALLOCATING:
        return defri

    elif phase is PHASE.WRITING:
        # ep_assert(_alloctable[obj] & 3 == 0)
        return RlocInt_C(_alloctable[_found_objects_dict[obj]], 4)

    else:
        raise EPError(_("Can't calculate object address now"))
