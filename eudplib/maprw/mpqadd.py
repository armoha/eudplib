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

from .. import utils as ut
import ctypes
import sys

_addedFiles = {}


def UpdateFileListByListfile(mpqr):
    """Use listfile to get list of already existing files."""

    _addedFiles.clear()

    flist = mpqr.EnumFiles()

    # no listfile -> add default listfile
    if not flist:
        flist = ["staredit\\scenario.chk", "(listfile)"]

    for fname in flist:
        MPQAddFile(fname, None)


def MPQAddFile(fname, content, isWave=False):
    """Add file/wave to output map.

    :param fname: Desired filename in mpq
    :param content: Content to put inside.
    :param isWave: Is file wave file? Wave file can be lossy compressed if this
        flag is set to True.

    .. note::
        This function may error if duplicate filenames is found. However, not
        all duplicated filenames are guaranteed to be catched here. Some of
        them may be catched at UpdateMPQ(internal) function.
    """

    # make fname case_insensitive
    fname_key = ut.u2b(fname.upper())

    ut.ep_assert(
        isinstance(content, bytes) or isinstance(content, bytearray) or content is None,
        "Invalid content type",
    )

    ut.ep_assert(fname_key not in _addedFiles, 'MPQ filename duplicate : "%s"' % fname)

    _addedFiles[fname_key] = (fname, content, isWave)


def MPQAddWave(fname, content):
    """Add wave to output map.

    :param fname: Desired filename in mpq
    :param content: Content to put inside.

    .. note:: See `MPQAddFile` for more info
    """
    return MPQAddFile(fname, content, True)


def UpdateMPQ(mpqw):
    """Really append additional mpq file to mpq file.

    `MPQAddFile` queues addition, and UpdateMPQ really adds them.
    """

    max_count = max(1024, 1 << (len(_addedFiles)).bit_length())
    setmax = mpqw.SetMaxFileCount(max_count)
    if not setmax:
        raise ctypes.WinError(ctypes.get_last_error())

    for fname, content, isWave in _addedFiles.values():
        if content is not None:
            if isWave:
                ret = mpqw.PutWave(ut.u2b(fname), content)
            else:
                ret = mpqw.PutFile(ut.u2b(fname), content)
            if not ret:
                print(
                    "Failed adding file %s to mpq: May be duplicate" % fname,
                    file=sys.stderr
                )
                raise ctypes.WinError(ctypes.get_last_error())


def GetAddedFiles():
    ret = set(fname for fname, content, isWave in _addedFiles.values())
    ret.add("staredit\scenario.chk")
    ret.add("(listfile)")
    return ret
