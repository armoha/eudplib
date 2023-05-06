#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from os import urandom

from ... import core as c
from ...core.allocator.payload import setPayloadLoggerMode
from ...core.mapdata.chktok import CHK
from ...utils.blockstru import BlockStruManager, set_blockstru_manager
from .injFinalizer import CreateInjectFinalizer
from .payloadInit import InitializePayload
from .payloadReloc import CreatePayloadRelocator
from .vectorReloc import CreateVectorRelocator

skip_payload_relocator = False


def PRT_SkipPayloadRelocator(enable: bool) -> None:
    global skip_payload_relocator
    skip_payload_relocator = enable


def applyInjector(chkt: CHK, root: c.Forward | c.RawTrigger) -> None:
    # Create injector triggers
    bsm = BlockStruManager()
    prev_bsm = set_blockstru_manager(bsm)
    if skip_payload_relocator:
        mrgndata = None
    else:
        mrgndata = urandom(5100)

    root = CreateInjectFinalizer(chkt, root, mrgndata)

    setPayloadLoggerMode(True)
    payload = c.CreatePayload(root)
    setPayloadLoggerMode(False)

    if skip_payload_relocator:
        payload = CreatePayloadRelocator(payload)
        CreateVectorRelocator(chkt, payload)
    else:
        InitializePayload(chkt, payload, mrgndata)

    set_blockstru_manager(prev_bsm)
