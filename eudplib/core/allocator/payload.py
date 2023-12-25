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

_payload_builder = allocator.PayloadBuilder()

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


def _collect_objects(root: "EUDObject | Forward") -> None:
    global phase
    global _payload_builder

    lprint(_("[Stage 1/3] CollectObjects"), flush=True)

    phase = PHASE_COLLECTING

    _payload_builder.collect_objects(root)

    # cleanup
    phase = 0

    # Final
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

    _payload_builder.alloc_objects()

    phase = 0


def _construct_payload() -> Payload:
    global phase
    global _payload_builder

    phase = PHASE_WRITING
    lprint(_("[Stage 3/3] ConstructPayload"), flush=True)
    if _payload_builder is None:
        raise EPError(_("PayloadBuilder is not instantiated"))

    payload = _payload_builder.construct_payload()
    phase = 0
    return Payload(*payload)


RegisterCreatePayloadCallback = _payload_builder.register_create_payload_callback
_register_after_collecting_callback = (
    _payload_builder.register_after_collecting_callback
)


def CreatePayload(root: "EUDObject | Forward") -> Payload:  # noqa: N802
    # Call callbacks
    _payload_builder.call_callbacks_on_create_payload()
    _collect_objects(root)
    _payload_builder.call_callbacks_after_collecting()
    _allocate_objects()
    return _construct_payload()


_PayloadBuffer: TypeAlias = (
    allocator.ObjCollector | allocator.ObjAllocator | allocator.PayloadBuffer
)
defri: RlocInt_C = RlocInt(0, 4)


def GetObjectAddr(obj: "EUDObject") -> RlocInt_C:  # noqa: N802
    global _payload_builder

    if phase == PHASE_COLLECTING:
        _payload_builder.collect_object(obj)
        return defri

    elif phase == PHASE_ALLOCATING:
        return defri

    elif phase == PHASE_WRITING:
        # ep_assert(_payload_builder.offset(obj) & 3 == 0)
        return RlocInt_C(_payload_builder.offset(obj), 4)  # type: ignore[union-attr]

    else:
        raise EPError(_("Can't calculate object address now"))
