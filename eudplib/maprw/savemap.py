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

from ..core.mapdata import mapdata, mpqapi
from ..core import RegisterCreatePayloadCallback
from .injector.applyInjector import applyInjector
from .inlinecode.ilcprocesstrig import PreprocessInlineCode
from .injector.mainloop import _MainStarter
from .mpqadd import UpdateMPQ
from ..core.eudfunc.trace.tracetool import _GetTraceMap, _ResetTraceMap
from .chkdiff import chkdiff

import binascii
import lzma
import simplecrypt

traceHeader = None
traceMap = []

patchPassword = None

def PRT_SetPatchPassword(password):
    global patchPassword
    patchPassword = password


def getTraceMap():
    global traceMap, traceHeader
    newTraceHeader, newTraceMap = _GetTraceMap()
    if newTraceMap:
        traceHeader = newTraceHeader
        traceMap = list(newTraceMap)
    _ResetTraceMap()


RegisterCreatePayloadCallback(getTraceMap)


def SaveMap(fname, rootf):
    """Save output map with root function.

    :param fname: Path for output map.
    :param rootf: Main entry function.
    """

    print("Saving to %s..." % fname)
    chkt = mapdata.GetChkTokenized()

    _ResetTraceMap()

    # Add payload
    root = _MainStarter(rootf)
    PreprocessInlineCode(chkt)
    mapdata.UpdateMapData()

    applyInjector(chkt, root)

    chkt.optimize()
    rawchk = chkt.savechk()
    print("Output scenario.chk : %.3fMB" % (len(rawchk) / 1000000))

    # Process by modifying existing mpqfile
    open(fname, "wb").write(mapdata.GetRawFile())

    mw = mpqapi.MPQ()
    mw.Open(fname)
    mw.PutFile("staredit\\scenario.chk", rawchk)

    # Get diff
    if patchPassword:
        print('[U] Patch-based unprotection enabled.')
        origchkt = mapdata.GetOriginalChkTokenized()
        print(' 1. Calculating bsdiff btw original & new chk')
        diff = chkdiff(origchkt, chkt)
        print(' 2. Compressing')
        diff = lzma.compress(diff)
        print(' 3. Encrypting')
        diff = simplecrypt.encrypt(patchPassword, diff)
        mw.PutFile("staredit\\scenario.chk.patch", diff)

    UpdateMPQ(mw)
    mw.Compact()
    mw.Close()

    if traceMap:
        traceFname = fname + ".epmap"
        print("Writing trace file to %s" % traceFname)
        with open(traceFname, "w", encoding="utf-8") as wf:
            wf.write("H0: %s\n" % binascii.hexlify(traceHeader[0]).decode("ascii"))
            wf.write("H1: %s\n" % binascii.hexlify(traceHeader[1]).decode("ascii"))
            for k, v in traceMap:
                wf.write(" - %08X : %s\n" % (k, v))
