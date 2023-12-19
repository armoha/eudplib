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
from .pbuffer import Payload
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

    _alloctable, _payload_size = allocator.alloc_objects(_found_objects_dict)

    phase = None


# -------


def ConstructPayload() -> Payload:
    global phase

    phase = PHASE.WRITING
    lprint(_("[Stage 3/3] ConstructPayload"), flush=True)
    objn = len(_found_objects_dict)

    pbuf = allocator.PayloadBuffer(_payload_size)

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
    return Payload(*pbuf.CreatePayload())


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


_PayloadBuffer: TypeAlias = (
    ObjCollector | allocator.ObjAllocator | allocator.PayloadBuffer
)
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
