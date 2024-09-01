#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ... import utils as ut
from ...localize import _
from ..rawtrigger.consttype import ConstType
from .structarr import _EUDStructMetaclass
from .vararray import EUDVArray


class EUDStruct(ut.ExprProxy, metaclass=_EUDStructMetaclass):
    def __init__(self, *args, _from=None, _static_initval=None, **kwargs) -> None:
        super().__setattr__("_initialized", False)
        fieldcount = len(self._fielddict)

        if _from is not None:
            super().__init__(EUDVArray(fieldcount).cast(_from))
            self._initialized = True
        else:
            if _static_initval is None:  # hacky way...
                _static_initval = [0] * fieldcount
            super().__init__(EUDVArray(fieldcount)(_static_initval))
            self._initialized = True
            self.constructor_static(*args, **kwargs)

    # Helper function for alloc & free
    # Due to cyclic dependency we import objpool inside methods
    @classmethod
    def alloc(cls, *args, **kwargs):
        from ...collections.objpool import get_global_pool

        return get_global_pool().alloc(cls, *args, **kwargs)

    @classmethod
    def free(cls, data):
        from ...collections.objpool import get_global_pool

        return get_global_pool().free(cls, data)

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
        """Create struct clone"""
        basetype = type(self)
        inst = basetype()
        self.copyto(inst)
        return inst

    def setall(self, values):
        self.fill(values, assert_expected_values_len=len(self._fielddict))

    def copyto(self, inst):
        """Copy struct to other instance"""
        for i, _nametype in enumerate(self._fielddict):
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
        attrid, attrtype = self._fielddict[name]
        if isinstance(attrtype, ConstType):
            value = attrtype.cast(value)
        self.set(attrid, value)

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            try:
                return self.getfield(name)
            except KeyError as e:
                raise AttributeError from e

    def __setattr__(self, name, value):
        if self._initialized:
            try:
                self.setfield(name, value)
            except KeyError:
                raise ut.EPError(_("Unknown field name {}").format(name))
        else:
            super().__setattr__(name, value)

    # Utilities

    def __lshift__(self, rhs):
        raise ut.EPError(_("Cannot reassign another value to eudstruct."))

    # Specializations

    def iaddattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.iadditem(attrid, value)

    # FIXME: add operator for Subtract
    def isubtractattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.isubtractitem(attrid, value)

    def isubattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.isubitem(attrid, value)

    def imulattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.imulitem(attrid, value)

    def ifloordivattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.ifloordivitem(attrid, value)

    def imodattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.imoditem(attrid, value)

    def ilshiftattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.ilshiftitem(attrid, value)

    def irshiftattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.irshiftitem(attrid, value)

    def ipowattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.ipowitem(attrid, value)

    def iandattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.ianditem(attrid, value)

    def iorattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.ioritem(attrid, value)

    def ixorattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.ixoritem(attrid, value)

    # FIXME: Add operator for x[i] = ~x[i]
    def iinvertattr(self, name, value):
        attrid, _ = self._fielddict[name]
        self.iinvertitem(attrid, value)

    # Attribute comparisons

    def eqattr(self, name, value):
        attrid, _ = self._fielddict[name]
        return self.eqitem(attrid, value)

    def neattr(self, name, value):
        attrid, _ = self._fielddict[name]
        return self.neitem(attrid, value)

    def leattr(self, name, value):
        attrid, _ = self._fielddict[name]
        return self.leitem(attrid, value)

    def geattr(self, name, value):
        attrid, _ = self._fielddict[name]
        return self.geitem(attrid, value)

    def ltattr(self, name, value):
        attrid, _ = self._fielddict[name]
        return self.ltitem(attrid, value)

    def gtattr(self, name, value):
        attrid, _ = self._fielddict[name]
        return self.gtitem(attrid, value)
