#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import ctypes
import sys

from .. import utils as ut
from ..core.mapdata.mpqapi import MPQ
from ..localize import _

_addedFiles: dict[bytes, tuple[str, bytes | None, bool]] = {}


def UpdateFileListByListfile(mpqr: MPQ) -> None:
    """Use listfile to get list of already existing files."""

    _addedFiles.clear()

    flist = mpqr.EnumFiles()

    # no listfile -> add default listfile
    if not flist:
        flist = ["staredit\\scenario.chk", "(listfile)"]

    for fname in flist:
        MPQAddFile(fname, None)


def MPQCheckFile(fname: str) -> bytes:
    """Check if filename is already exist.

    :param fname: Desired filename in mpq
    """

    # make fname case_insensitive
    from ntpath import normcase, normpath

    fname_key = ut.u2b(normpath(normcase(fname)))

    ut.ep_assert(fname_key not in _addedFiles, _('MPQ filename duplicate : "{}"').format(fname))

    return fname_key


def MPQAddFile(fname: str, content: bytes | None, isWave: bool = False) -> None:
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

    ut.ep_assert(
        isinstance(content, bytes) or isinstance(content, bytearray) or content is None,
        _("Invalid content type"),
    )

    # make fname case_insensitive
    fname_key = MPQCheckFile(fname)

    _addedFiles[fname_key] = (fname, content, isWave)


def MPQAddWave(fname: str, content: bytes | None) -> None:
    """Add wave to output map.

    :param fname: Desired filename in mpq
    :param content: Content to put inside.

    .. note:: See `MPQAddFile` for more info
    """
    MPQAddFile(fname, content, True)


def UpdateMPQ(mpqw: MPQ) -> None:
    """Really append additional mpq file to mpq file.

    `MPQAddFile` queues addition, and UpdateMPQ really adds them.
    """

    count = mpqw.GetMaxFileCount()
    if count < len(_addedFiles):  # need to increase max file count
        max_count = max(1024, 1 << (len(_addedFiles)).bit_length())
        is_increased = mpqw.SetMaxFileCount(max_count)
        if not is_increased:
            raise ctypes.WinError(ctypes.get_last_error())

    for fname, content, isWave in _addedFiles.values():
        if content is not None:
            ret: int | None
            if isWave:
                ret = mpqw.PutWave(fname, content)
            else:
                ret = mpqw.PutFile(fname, content)
            if not ret:
                ut.ep_eprint(_("Failed adding file {} to mpq: May be duplicate").format(fname))
                raise ctypes.WinError(ctypes.get_last_error())


def GetAddedFiles() -> set[str]:
    ret = set(fname for fname, content, isWave in _addedFiles.values())
    ret.add("staredit\\scenario.chk")
    ret.add("(listfile)")
    return ret
