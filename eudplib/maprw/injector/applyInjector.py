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

from ... import core as c
from ...core.allocator.payload import setPayloadLoggerMode
from ...utils.blockstru import BlockStruManager, SetCurrentBlockStruManager

from .vectorReloc import CreateVectorRelocator
from .payloadReloc import CreatePayloadRelocator
from .injFinalizer import CreateInjectFinalizer
from .payloadInit import InitializePayload

from os import urandom


skip_payload_relocator = False


def PRT_SkipPayloadRelocator(enable):
    global skip_payload_relocator
    skip_payload_relocator = enable


def applyInjector(chkt, root):
    # Create injector triggers
    bsm = BlockStruManager()
    prev_bsm = SetCurrentBlockStruManager(bsm)
    obfus_mrgn = urandom(5100)

    root = CreateInjectFinalizer(chkt, root, obfus_mrgn)

    setPayloadLoggerMode(True)
    payload = c.CreatePayload(root)
    setPayloadLoggerMode(False)

    if skip_payload_relocator:
        payload = CreatePayloadRelocator(payload)
        CreateVectorRelocator(chkt, payload)
    else:
        InitializePayload(chkt, payload, obfus_mrgn)

    SetCurrentBlockStruManager(prev_bsm)
