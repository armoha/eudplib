# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os
import struct
import sys
from ctypes import (
    POINTER,
    Structure,
    byref,
    c_char_p,
    c_int,
    c_void_p,
    c_wchar_p,
    create_string_buffer,
    sizeof,
)
from tempfile import NamedTemporaryFile

from ...localize import _
from ...utils import EPError, b2u, b2utf8, find_data_file, u2b, u2utf8

# Constants
MPQ_FILE_COMPRESS = 0x00000200
MPQ_FILE_ENCRYPTED = 0x00010000
MPQ_FILE_FIX_KEY = 0x00020000
MPQ_FILE_REPLACEEXISTING = 0x80000000
MPQ_COMP_ZLIB = 0x00000002

if sys.platform.startswith("win32"):  # windows
    from ctypes import WinDLL as DLL  # noqa: N814
else:  # elif sys.platform.startswith("darwin")  # mac
    from ctypes import CDLL as DLL

libstorm: DLL | None = None


class CreateInfo(Structure):
    _fields_ = [  # noqa: RUF012
        ("cbSize", c_int),
        ("dwMpqVersion", c_int),
        ("pvUserData", c_void_p),
        ("cbUserData", c_int),
        ("dwStreamFlags", c_int),
        ("dwFileFlags1", c_int),
        ("dwFileFlags2", c_int),
        ("dwFileFlags3", c_int),
        ("dwAttrFlags", c_int),
        ("dwSectorSize", c_int),
        ("dwRawChunkSize", c_int),
        ("dwMaxFileCount", c_int),
    ]


def _init_mpq_library() -> None:
    global libstorm

    try:
        if sys.platform.startswith("win32"):  # windows
            if struct.calcsize("P") == 4:  # 32bit
                libstorm = DLL(
                    find_data_file("StormLib32.dll", __file__),
                    use_last_error=True,
                )
            else:  # 64bit
                libstorm = DLL(
                    find_data_file("StormLib64.dll", __file__),
                    use_last_error=True,
                )

        else:  # elif sys.platform.startswith("darwin"):  # mac
            try:
                libstorm = DLL("libstorm.dylib", use_last_error=True)
            except OSError as exc:
                raise EPError(
                    _("You need to install stormlib before using eudplib."),
                    " $ brew install homebrew/games/stormlib",
                    sep="\n",
                ) from exc

        # for MpqRead
        libstorm.SFileOpenArchive.restype = c_int
        libstorm.SFileCloseArchive.restype = c_int
        libstorm.SFileOpenFileEx.restype = c_int
        libstorm.SFileGetFileSize.restype = c_int
        libstorm.SFileReadFile.restype = c_int
        libstorm.SFileCloseFile.restype = c_int

        libstorm.SFileOpenArchive.argtypes = [
            c_wchar_p,
            c_int,
            c_int,
            c_void_p,
        ]
        libstorm.SFileCloseArchive.argtypes = [c_void_p]
        libstorm.SFileOpenFileEx.argtypes = [
            c_void_p,
            c_char_p,
            c_int,
            c_void_p,
        ]
        libstorm.SFileGetFileSize.argtypes = [c_void_p, c_void_p]
        libstorm.SFileReadFile.argtypes = [
            c_void_p,
            c_char_p,
            c_int,
            c_void_p,
            c_int,
        ]
        libstorm.SFileCloseFile.argtypes = [c_void_p]

        # for MpqWrite
        libstorm.SFileCompactArchive.restype = c_int
        libstorm.SFileCreateArchive2.restype = c_int
        libstorm.SFileAddFileEx.restype = c_int
        libstorm.SFileGetMaxFileCount.restype = c_int
        libstorm.SFileSetMaxFileCount.restype = c_int

        libstorm.SFileCompactArchive.argtypes = [c_void_p, c_char_p, c_int]
        libstorm.SFileCreateArchive2.argtypes = [
            c_wchar_p,
            POINTER(CreateInfo),
            c_void_p,
        ]
        libstorm.SFileAddFileEx.argtypes = [
            c_void_p,
            c_wchar_p,
            c_char_p,
            c_int,
            c_int,
            c_int,
        ]
        libstorm.SFileGetMaxFileCount.argtypes = [c_void_p]
        libstorm.SFileSetMaxFileCount.argtypes = [c_void_p, c_int]

    except OSError as exc:
        raise EPError(_("Loading StormLib failed.")) from exc


class MPQ:
    def __init__(self) -> None:
        if libstorm is None:
            raise EPError(_("Loading StormLib failed."))
        self.mpqh: c_void_p | None = None
        self.libstorm: DLL = libstorm

    def __del__(self) -> None:
        self.Close()

    def Open(self, fname: str) -> bool:  # noqa: N802
        if self.mpqh is not None:
            raise RuntimeError(_("Duplicate opening"))

        h = c_void_p()
        ret = self.libstorm.SFileOpenArchive(fname, 0, 0, byref(h))
        if not ret:
            self.mpqh = None
            return False

        self.mpqh = h
        return True

    def Create(  # noqa: N802
        self, fname: str, *, sector_size: int = 3, file_count: int = 1024
    ) -> bool:
        if self.mpqh is not None:
            raise RuntimeError(_("Duplicate opening"))

        cinfo = CreateInfo()
        cinfo.cbSize = sizeof(CreateInfo)
        cinfo.dwMpqVersion = 0
        cinfo.dwStreamFlags = 0
        cinfo.dwFileFlags1 = 0
        cinfo.dwFileFlags2 = 0
        cinfo.dwFileFlags3 = 0
        cinfo.dwAttrFlags = 0
        cinfo.dwSectorSize = 2 ** (9 + sector_size)
        cinfo.dwMaxFileCount = file_count
        h = c_void_p()
        ret = self.libstorm.SFileCreateArchive2(fname, byref(cinfo), byref(h))
        if not ret:
            self.mpqh = None
            return False

        self.mpqh = h
        return True

    def Close(self) -> None:  # noqa: N802
        if self.mpqh is None:
            return

        self.libstorm.SFileCloseArchive(self.mpqh)
        self.mpqh = None

    def EnumFiles(self) -> list[str]:  # noqa: N802
        # using listfile.
        lst = self.Extract("(listfile)")
        if lst is None:
            return []

        try:
            return b2u(lst).replace("\r", "").split("\n")
        except UnicodeDecodeError:
            try:
                return b2utf8(lst).replace("\r", "").split("\n")
            except UnicodeDecodeError:
                return []

    # Extract
    def Extract(self, fname: str) -> bytes | None:  # noqa: N802
        if self.libstorm is None:
            return None
        elif not self.mpqh:
            return None
        elif not fname:
            return None

        # Open file
        fileh = c_void_p()
        ret = self.libstorm.SFileOpenFileEx(self.mpqh, u2b(fname), 0, byref(fileh))
        if not ret:
            ret = self.libstorm.SFileOpenFileEx(
                self.mpqh, u2utf8(fname), 0, byref(fileh)
            )
            if not ret:
                return None

        # Get file size & allocate buffer
        # Note : this version only supports 32bit mpq file
        fsize = self.libstorm.SFileGetFileSize(fileh, 0)
        if not fsize or fsize <= 0:
            return None
        fdata = create_string_buffer(fsize)

        # Read file
        pfread = c_int()
        self.libstorm.SFileReadFile(fileh, fdata, fsize, byref(pfread), 0)
        self.libstorm.SFileCloseFile(fileh)

        if pfread.value == fsize:
            return fdata.raw
        else:
            return None

    # Writer

    def PutFile(  # noqa: N802
        self,
        fname: str,
        buffer: bytes,
        *,
        cmp1: int = MPQ_COMP_ZLIB,
        cmp2: int = MPQ_COMP_ZLIB,
    ):
        if not self.mpqh:
            return None

        # Create temporary file
        f = NamedTemporaryFile(delete=False)
        f.write(bytes(buffer))
        tmpfname = f.name
        f.close()

        # Add to mpq
        ret = self.libstorm.SFileAddFileEx(
            self.mpqh,
            tmpfname,
            u2b(fname),
            MPQ_FILE_COMPRESS | MPQ_FILE_ENCRYPTED | MPQ_FILE_REPLACEEXISTING,
            cmp1,
            cmp2,
        )
        if not ret:
            self.libstorm.SFileAddFileEx(
                self.mpqh,
                tmpfname,
                u2utf8(fname),
                MPQ_FILE_COMPRESS | MPQ_FILE_ENCRYPTED | MPQ_FILE_REPLACEEXISTING,
                cmp1,
                cmp2,
            )
        os.unlink(tmpfname)
        return ret

    def PutWave(  # noqa: N802
        self,
        fname: str,
        buffer: bytes,
        *,
        cmp1: int = MPQ_COMP_ZLIB,
        cmp2: int = MPQ_COMP_ZLIB,
    ) -> int | None:
        if not self.mpqh:
            return None

        # Create temporary file
        f = NamedTemporaryFile(delete=False)
        f.write(bytes(buffer))
        tmpfname = f.name
        f.close()

        # Add to mpq
        ret = self.libstorm.SFileAddFileEx(
            self.mpqh,
            os.fsencode(tmpfname),
            u2b(fname),
            MPQ_FILE_COMPRESS | MPQ_FILE_ENCRYPTED,
            cmp1,
            cmp2,
        )
        if not ret:
            ret = self.libstorm.SFileAddFileEx(
                self.mpqh,
                os.fsencode(tmpfname),
                u2utf8(fname),
                MPQ_FILE_COMPRESS | MPQ_FILE_ENCRYPTED,
                cmp1,
                cmp2,
            )
        os.unlink(tmpfname)
        return ret

    def GetMaxFileCount(self) -> int:  # noqa: N802
        return self.libstorm.SFileGetMaxFileCount(self.mpqh)

    def SetMaxFileCount(self, count: int) -> int:  # noqa: N802
        return self.libstorm.SFileSetMaxFileCount(self.mpqh, count)

    def Compact(self) -> int:  # noqa: N802
        return self.libstorm.SFileCompactArchive(self.mpqh, None, 0)


_init_mpq_library()

if __name__ == "__main__":
    mr = MPQ()
    mr.Open("basemap.scx")
    a = mr.Extract("staredit\\scenario.chk")
    mr.Close()
    if a is None:
        raise EPError("failed to extract staredit\\scenario.chk of basemap.scx")
    print(len(a))

    if os.path.exists("test.scx"):
        os.unlink("test.scx")
    open("test.scx", "wb").write(open("basemap.scx", "rb").read())

    mr.Open("test.scx")
    a = mr.Extract("staredit\\scenario.chk")
    if a is None:
        raise EPError("failed to extract staredit\\scenario.chk of test.scx")
    print(len(a))
    mr.PutFile("test", b"1234")
    b = mr.Extract("test")
    mr.Compact()
    print(b)
