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
from .inj_finalizer import create_inject_finalizer
from .payload_init import initialize_payload
from .payload_reloc import create_payload_relocator
from .vector_reloc import create_vector_relocator

skip_payload_relocator = False


def PRT_SkipPayloadRelocator(enable: bool) -> None:  # noqa: N802
    global skip_payload_relocator
    skip_payload_relocator = enable


def apply_injector(chkt: CHK, root: c.Forward | c.RawTrigger) -> None:
    # Create injector triggers
    bsm = BlockStruManager()
    prev_bsm = set_blockstru_manager(bsm)
    if skip_payload_relocator:
        mrgndata = None
    else:
        mrgndata = urandom(5100)

    root = create_inject_finalizer(chkt, root, mrgndata)

    setPayloadLoggerMode(True)
    payload = c.CreatePayload(root)
    setPayloadLoggerMode(False)

    if skip_payload_relocator:
        payload = create_payload_relocator(payload)
        create_vector_relocator(chkt, payload)
    else:
        initialize_payload(chkt, payload, mrgndata)

    set_blockstru_manager(prev_bsm)
