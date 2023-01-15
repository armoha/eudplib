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

from abc import ABCMeta, abstractmethod

from eudplib import utils as ut

from ..allocator import ConstExpr, RlocInt_C
from ..allocator.payload import GetObjectAddr, _PayloadBuffer


class EUDObject(ConstExpr, metaclass=ABCMeta):
    """Class for standalone object on memory

    .. note::
        Object collection occures in three steps:

        - Collection phase : collects object used in map generation. Object
        used in WritePayload method are being collected. Methods Evaluate
        and WritePayload are called during this phase.
        - Allocation phase : Object have their offset assigned. GetDataSize
        method is called on this phase, so if GetDataSize is being called,
        it means that every object required in map has been collected.
        WritePayload and GetDataSize method should behave exactly the same as
        it should on Writing phase here.
        - Writing phase : Object is written into payload.
    """

    def __init__(self) -> None:
        super().__init__(self)

    def DynamicConstructed(self) -> bool:
        """Whether function is constructed dynamically.

        Dynamically constructed EUDObject may have their dependency list
        generated during object construction. So their dependency list is
        re-examined before allocation phase.
        """
        return False

    def Evaluate(self) -> RlocInt_C:
        """
        What this object should be evaluated to when used in eudplib program.

        :return: Default) Memory address of this object.

        .. note::
            In overriding this method, you can use
            :func:`eudplib.GetObjectAddr`.
        """
        return GetObjectAddr(self)

    @abstractmethod
    def GetDataSize(self) -> int:
        """Memory size of object."""
        raise NotImplementedError()

    def CollectDependency(self, pbuffer: _PayloadBuffer) -> None:
        self.WritePayload(pbuffer)

    @abstractmethod
    def WritePayload(self, pbuffer: _PayloadBuffer) -> None:
        """Write object"""
        raise NotImplementedError()
