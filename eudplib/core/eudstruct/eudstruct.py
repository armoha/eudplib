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

from ... import utils as ut
from ...localize import _
from ..allocator import IsConstExpr
from ..variable import EUDVariable
from .vararray import EUDVArray
from .structarr import _EUDStruct_Metaclass


class EUDStruct(ut.ExprProxy, metaclass=_EUDStruct_Metaclass):
    def __init__(self, *args, _from=None, **kwargs):
        basetype = type(self)
        fields = basetype._fields_
        fieldn = len(fields)

        # Fill fielddict
        fielddict = {}
        for index, nametype in enumerate(fields):
            if isinstance(nametype, str):
                fielddict[nametype] = (index, None)
            else:
                fielddict[nametype[0]] = (index, nametype[1])
        self._fielddict = fielddict

        if _from is not None:
            super().__init__(EUDVArray(fieldn).cast(_from))
            self._initialized = True
        else:
            super().__init__(EUDVArray(fieldn)([0] * len(fields)))
            self.isPooled = False
            self._initialized = True
            self.constructor_static(*args, **kwargs)

    # Helper function for alloc & free
    # Due to cyclic dependency we import objpool inside methods
    @classmethod
    def alloc(cls, *args, **kwargs):
        from ...eudlib.objpool import GetGlobalPool

        return GetGlobalPool().alloc(cls, *args, **kwargs)

    @classmethod
    def free(cls, data):
        from ...eudlib.objpool import GetGlobalPool

        return GetGlobalPool().free(cls, data)

    # Constructor & Destructor of classes
    def constructor(self):
        """Constructor for individual structures.

        Default constructor accepts no arguments, but derived classes may
        accept additional arguments.

        This function is called when
            - Argument is allocated from pool   (self.isPooled = True)
            - Argument is generated             (self.isPooled = False)

        You may choose to either allocate member from pool or just allocate
        members statically via self.isPooled.
        """
        pass

    def constructor_static(self, *args, **kwargs):
        """Specialized constructor for static variables.

        Static variable may not require allocation for member variables.
        Function may specialize their behavior by overriding this function"""
        self.constructor(*args, **kwargs)

    def destructor(self):
        """Destructor for individual structures.

        Destructor accepts no arguments. Destructor is called when
            - Manually called. (Ex: stack variable)
            - free() is called for object
        """
        pass

    @classmethod
    def cast(cls, _from):
        try:
            return cls(_from=_from)
        except TypeError:
            obj = cls.__new__(cls)
            EUDStruct.__init__(obj, _from=_from)

    # Initializer

    def copy(self):
        """ Create struct clone """
        basetype = type(self)
        inst = basetype()
        self.copyto(inst)
        return inst

    def setall(self, values):
        self.fill(values, assert_expected_values_len=len(self._fielddict))

    def copyto(self, inst):
        """ Copy struct to other instance """
        basetype = type(self)
        fields = basetype._fields_
        for i, nametype in enumerate(fields):
            inst.set(i, self.get(i))

    # Field setter & getter

    def getfield(self, name):
        attrid, attrtype = self._fielddict[name]
        attr = self.get(attrid)
        if attrtype:
            return attrtype.cast(attr)
        else:
            return attr

    def setfield(self, name, value):
        attrid, _ = self._fielddict[name]
        self.set(attrid, value)

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            try:
                return self.getfield(name)
            except KeyError as e:
                raise AttributeError(e)

    def __setattr__(self, name, value):
        if "_initialized" in self.__dict__:
            try:
                self.setfield(name, value)
            except KeyError as e:
                raise ut.EPError(_("Unknown field name {}").format(name))
        else:
            self.__dict__[name] = value

    # Utilities

    def asVariable(self):
        if IsConstExpr(self):
            var = EUDVariable(self)
        else:
            var = EUDVariable()
            var << self
        return type(self)(var)

    def __lshift__(self, rhs):
        raise ut.EPError(_("Cannot reassign another value to eudstruct."))
