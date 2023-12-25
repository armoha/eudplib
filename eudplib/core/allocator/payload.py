#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import time
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeAlias

from eudplib.bindings._rust import allocator
from eudplib.localize import _
from eudplib.utils import EPError, _rand_lst, ep_assert

from .constexpr import Evaluable, Evaluate, Forward
from .pbuffer import Payload
from .rlocint import RlocInt, RlocInt_C

if TYPE_CHECKING:
    from ..eudobj import EUDObject

_found_objects_dict: "dict[EUDObject, int]" = {}
_untraversed_objects: "list[EUDObject]" = []
_dynamic_objects_set: "set[EUDObject]" = set()
_payload_builder: allocator.PayloadBuilder | None = None

PHASE_COLLECTING = 1
PHASE_ALLOCATING = 2
PHASE_WRITING = 3
phase: int = 0

_payload_compress: bool = False
_payload_shuffle: bool = True

# -------

_last_time: float = 0.0
_is_logging_enabled: bool = False


def _set_payload_logger_mode(mode: bool) -> None:
    global _is_logging_enabled
    _is_logging_enabled = mode


def lprint(text: str, flush: bool = False):
    global _last_time, _is_logging_enabled
    if not _is_logging_enabled:
        return

    current_time = time.time()
    if flush or (current_time - _last_time) >= 0.5:
        _last_time = current_time
        print(text, end="\n" if flush else "\r")


def CompressPayload(mode: bool) -> None:  # noqa: N802
    """Set payload compression mode.

    :param mode: If true, enable object stacking (compression). If false,
    disable it.
    """
    global _payload_compress
    ep_assert(mode in (True, False), _("Invalid type") + f": {mode}")
    _payload_compress = True if mode else False


def ShufflePayload(mode: bool) -> None:  # noqa: N802
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
    calling object.CollectDependency() for every related objects.
    """

    def __init__(self) -> None:
        pass

    def StartWrite(self) -> None:  # noqa: N802
        pass

    def EndWrite(self) -> None:  # noqa: N802
        pass

    def WriteByte(self, number: int) -> None:  # noqa: N802
        pass

    def WriteWord(self, number: int) -> None:  # noqa: N802
        pass

    def WriteDword(self, obj: Evaluable) -> None:  # noqa: N802
        if not isinstance(obj, int):
            Evaluate(obj)

    def WritePack(self, structformat: str, arglist: list[Evaluable]) -> None:  # noqa: N802
        for arg in arglist:
            if not isinstance(arg, int):
                Evaluate(arg)

    def WriteBytes(self, b: bytes) -> None:  # noqa: N802
        pass

    def WriteSpace(self, spacesize: int) -> None:  # noqa: N802
        pass


def _collect_objects(root: "EUDObject | Forward") -> None:
    global phase
    global _found_objects_dict
    global _dynamic_objects_set
    global _untraversed_objects

    lprint(_("[Stage 1/3] CollectObjects"), flush=True)

    phase = PHASE_COLLECTING

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
        _found_objects_dict = {
            obj: i for i, obj in enumerate(reversed(found_objects))
        }

    # cleanup
    phase = 0

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


def _allocate_objects() -> None:
    global phase
    global _payload_builder

    phase = PHASE_ALLOCATING
    lprint(_("[Stage 2/3] AllocObjects"), flush=True)

    if not _payload_compress:
        raise EPError("CompressPayload(False) is currently not supported")

    _payload_builder = allocator.PayloadBuilder()
    _payload_builder.alloc_objects(_found_objects_dict)

    phase = 0


def _construct_payload() -> Payload:
    global phase
    global _payload_builder

    phase = PHASE_WRITING
    lprint(_("[Stage 3/3] ConstructPayload"), flush=True)
    if _payload_builder is None:
        raise EPError(_("PayloadBuilder is not instantiated"))

    payload = _payload_builder.construct_payload(_found_objects_dict)
    phase = 0
    return Payload(*payload)


_on_create_payload_callbacks: list[Callable] = []
_on_alloc_objects_callbacks: list[Callable] = []


def RegisterCreatePayloadCallback(f: Callable) -> None:  # noqa: N802
    _on_create_payload_callbacks.append(f)


def _RegisterAllocObjectsCallback(f: Callable) -> None:  # noqa: N802
    _on_alloc_objects_callbacks.append(f)


def CreatePayload(root: "EUDObject | Forward") -> Payload:  # noqa: N802
    # Call callbacks
    for f in _on_create_payload_callbacks:
        f()
    _collect_objects(root)
    for f in _on_alloc_objects_callbacks:
        f()
    _allocate_objects()
    return _construct_payload()


_PayloadBuffer: TypeAlias = (
    ObjCollector | allocator.ObjAllocator | allocator.PayloadBuffer
)
defri: RlocInt_C = RlocInt(0, 4)


def GetObjectAddr(obj: "EUDObject") -> RlocInt_C:  # noqa: N802
    global _payload_builder
    global _found_objects_dict
    global _untraversed_objects
    global _dynamic_objects_set

    if phase == PHASE_COLLECTING:
        if obj not in _found_objects_dict:
            _untraversed_objects.append(obj)
            _found_objects_dict[obj] = len(_found_objects_dict)
            if obj.DynamicConstructed():
                _dynamic_objects_set.add(obj)

        return defri

    elif phase == PHASE_ALLOCATING:
        return defri

    elif phase == PHASE_WRITING:
        # ep_assert(_payload_builder.offset(_found_objects_dict[obj]) & 3 == 0)
        return RlocInt_C(_payload_builder.offset(_found_objects_dict[obj]), 4)  # type: ignore[union-attr]

    else:
        raise EPError(_("Can't calculate object address now"))
