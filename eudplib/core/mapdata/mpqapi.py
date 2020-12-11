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

from ctypes import (
    c_int,
    c_char_p,
    c_void_p,
    create_string_buffer,
    byref,
    Structure,
    POINTER,
    sizeof,
)
import os
import struct
import platform
from tempfile import NamedTemporaryFile
from eudplib.localize import _
from eudplib.utils import u2b, u2utf8, b2u, ep_eprint, find_data_file


filename_u2b = None


# Constants
MPQ_FILE_COMPRESS = 0x00000200
MPQ_FILE_ENCRYPTED = 0x00010000
MPQ_FILE_FIX_KEY = 0x00020000
MPQ_FILE_REPLACEEXISTING = 0x80000000
MPQ_COMP_ZLIB = 0x00000002

libstorm = None


class CreateInfo(Structure):
    _fields_ = [
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


def InitMpqLibrary():
    global libstorm, filename_u2b

    try:
        platformName = platform.system()
        if platformName == "Windows":  # windows
            from ctypes import WinDLL

            if struct.calcsize("P") == 4:  # 32bit
                libstorm = WinDLL(
                    find_data_file("StormLib32.dll", __file__), use_last_error=True
                )
            else:  # 64bit
                libstorm = WinDLL(
                    find_data_file("StormLib64.dll", __file__), use_last_error=True
                )
            filename_u2b = u2b

        elif platformName == "Darwin":  # mac
            from ctypes import CDLL

            try:
                libstorm = CDLL("libstorm.dylib", use_last_error=True)
                filename_u2b = u2utf8
            except OSError as e:
                ep_eprint(
                    _("You need to install stormlib before using eudplib."),
                    " $ brew install homebrew/games/stormlib",
                    sep="\n",
                )
                raise

        # for MpqRead
        libstorm.SFileOpenArchive.restype = c_int
        libstorm.SFileCloseArchive.restype = c_int
        libstorm.SFileOpenFileEx.restype = c_int
        libstorm.SFileGetFileSize.restype = c_int
        libstorm.SFileReadFile.restype = c_int
        libstorm.SFileCloseFile.restype = c_int

        libstorm.SFileOpenArchive.argtypes = [c_char_p, c_int, c_int, c_void_p]
        libstorm.SFileCloseArchive.argtypes = [c_void_p]
        libstorm.SFileOpenFileEx.argtypes = [c_void_p, c_char_p, c_int, c_void_p]
        libstorm.SFileGetFileSize.argtypes = [c_void_p, c_void_p]
        libstorm.SFileReadFile.argtypes = [c_void_p, c_char_p, c_int, c_void_p, c_int]
        libstorm.SFileCloseFile.argtypes = [c_void_p]

        # for MpqWrite
        libstorm.SFileCompactArchive.restype = c_int
        libstorm.SFileCreateArchive2.restype = c_int
        libstorm.SFileAddFileEx.restype = c_int
        libstorm.SFileGetMaxFileCount.restype = c_int
        libstorm.SFileSetMaxFileCount.restype = c_int

        libstorm.SFileCompactArchive.argtypes = [c_void_p, c_char_p, c_int]
        libstorm.SFileCreateArchive2.argtypes = [
            c_char_p,
            POINTER(CreateInfo),
            c_void_p,
        ]
        libstorm.SFileAddFileEx.argtypes = [
            c_void_p,
            c_char_p,
            c_char_p,
            c_int,
            c_int,
            c_int,
        ]
        libstorm.SFileGetMaxFileCount.argtypes = [c_void_p]
        libstorm.SFileSetMaxFileCount.argtypes = [c_void_p, c_int]

        return True

    except OSError:
        ep_eprint(_("Loading StormLib failed."))
        raise


class MPQ:
    def __init__(self):
        self.mpqh = None
        self.libstorm = libstorm

    def __del__(self):
        self.Close()

    def Open(self, fname):
        if self.mpqh is not None:
            raise RuntimeError(_("Duplicate opening"))

        h = c_void_p()
        ret = self.libstorm.SFileOpenArchive(filename_u2b(fname), 0, 0, byref(h))
        if not ret:
            self.mpqh = None
            return False

        self.mpqh = h
        return True

    def Create(self, fname, *, sectorSize=3, fileCount=1024):
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
        cinfo.dwSectorSize = 2 ** (9 + sectorSize)
        cinfo.dwMaxFileCount = fileCount
        h = c_void_p()
        ret = self.libstorm.SFileCreateArchive2(
            filename_u2b(fname), byref(cinfo), byref(h)
        )
        if not ret:
            self.mpqh = None
            return False

        self.mpqh = h
        return True

    def Close(self):
        if self.mpqh is None:
            return None

        self.libstorm.SFileCloseArchive(self.mpqh)
        self.mpqh = None
        return True

    def EnumFiles(self):
        # using listfile.
        lst = self.Extract("(listfile)")
        if lst is None:
            return []

        try:
            return b2u(lst).replace("\r", "").split("\n")
        except UnicodeDecodeError:
            return []

    # Extract
    def Extract(self, fname):
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

    def PutFile(self, fname, buffer, *, cmp1=MPQ_COMP_ZLIB, cmp2=MPQ_COMP_ZLIB):
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
            filename_u2b(tmpfname),
            u2b(fname),
            MPQ_FILE_COMPRESS | MPQ_FILE_ENCRYPTED | MPQ_FILE_REPLACEEXISTING,
            cmp1,
            cmp2,
        )
        os.unlink(tmpfname)
        return ret

    def PutWave(self, fname, buffer, *, cmp1=MPQ_COMP_ZLIB, cmp2=MPQ_COMP_ZLIB):
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
            filename_u2b(tmpfname),
            u2b(fname),
            MPQ_FILE_COMPRESS | MPQ_FILE_ENCRYPTED,
            cmp1,
            cmp2,
        )
        os.unlink(tmpfname)
        return ret

    def GetMaxFileCount(self):
        return self.libstorm.SFileGetMaxFileCount(self.mpqh)

    def SetMaxFileCount(self, count):
        return self.libstorm.SFileSetMaxFileCount(self.mpqh, count)

    def Compact(self):
        return self.libstorm.SFileCompactArchive(self.mpqh, None, 0)


InitMpqLibrary()

if __name__ == "__main__":
    mr = MPQ()
    mr.Open("basemap.scx")
    a = mr.Extract("staredit\\scenario.chk")
    mr.Close()
    print(len(a))

    if os.path.exists("test.scx"):
        os.unlink("test.scx")
    open("test.scx", "wb").write(open("basemap.scx", "rb").read())

    mr.Open("test.scx")
    a = mr.Extract("staredit\\scenario.chk")
    print(len(a))
    mr.PutFile("test", b"1234")
    b = mr.Extract("test")
    mr.Compact()
    print(b)
