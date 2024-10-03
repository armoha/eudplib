# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
import os
from tempfile import NamedTemporaryFile

from .. import utils as ut
from ..bindings._rust import mpqapi
from ..localize import _

_addedFiles: dict[bytes, tuple[str, str | bytes | bytearray | None, bool]] = {}  # noqa: N816


def update_filelist_by_listfile(mpqr: mpqapi.MPQ) -> None:
    """Use listfile to get list of already existing files."""

    _addedFiles.clear()
    try:
        flist = mpqr.get_file_names_from_listfile()
    # no listfile -> add default listfile
    except Exception:
        flist = ["staredit\\scenario.chk", "(listfile)"]

    if not flist:
        flist = ["staredit\\scenario.chk", "(listfile)"]

    for fname in flist:
        MPQAddFile(fname, None)


def MPQCheckFile(fname: str) -> bytes:  # noqa: N802
    """Check if filename is already exist.

    :param fname: Desired filename in mpq
    """

    # make fname case_insensitive
    from ntpath import normcase, normpath

    fname_key = ut.u2b(normpath(normcase(fname)))

    ut.ep_assert(
        fname_key not in _addedFiles,
        _('MPQ filename duplicate : "{}"').format(fname),
    )

    return fname_key


def MPQAddFile(  # noqa: N802
    fname: str, path_or_content: str | bytes | bytearray | None, is_wav: bool = False
) -> None:
    """Add file/wave to output map.

    :param fname: Desired filename in mpq
    :param path_or_content: File path or content to put inside.
    :param is_wav: Is file wave file? Wave file can be lossy compressed if this
        flag is set to True.

    .. note::
        This function may error if duplicate filenames is found. However, not
        all duplicated filenames are guaranteed to be catched here. Some of
        them may be catched at _update_mpq(internal) function.
    """

    if not (
        isinstance(path_or_content, str | bytes | bytearray)
        or path_or_content is None
    ):
        raise ut.EPError(
            _("Invalid file path or content: {}").format(path_or_content)
        )

    # make fname case_insensitive
    fname_key = MPQCheckFile(fname)

    _addedFiles[fname_key] = (fname, path_or_content, is_wav)


def MPQAddWave(fname: str, path_or_content: str | bytes | bytearray | None) -> None:  # noqa: N802
    """Add wave to output map.

    :param fname: Desired filename in mpq
    :param path_or_content: File path or content to put inside.

    .. note:: See `MPQAddFile` for more info
    """
    MPQAddFile(fname, path_or_content, True)


def _update_mpq(mpqw: mpqapi.MPQ) -> None:
    """Really append additional mpq file to mpq file.

    `MPQAddFile` queues addition, and _update_mpq really adds them.
    """

    count = mpqw.get_max_file_count()
    if count < len(_addedFiles):  # need to increase max file count
        max_count = max(1024, 1 << (len(_addedFiles)).bit_length())
        try:
            mpqw.set_max_file_count(max_count)
        except Exception as e:
            raise ut.EPError(_("Failed to increase max file limit")) from e

    for fname, path_or_content, is_wav in _addedFiles.values():
        if path_or_content is None:
            continue

        if isinstance(path_or_content, str):
            file_path = path_or_content
        else:
            # Create temporary file
            f = NamedTemporaryFile(delete=False)
            f.write(bytes(path_or_content))
            file_path = f.name
            f.close()

        try:
            mpqw.add_file(fname, file_path)
        except Exception as e:
            raise ut.EPError(
                _("Failed adding file {} to mpq: May be duplicate").format(fname)
            ) from e

        if not isinstance(path_or_content, str):
            os.unlink(file_path)
