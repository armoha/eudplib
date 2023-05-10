#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ...utils import ExprProxy, EPError
from .selftype import selftype
from .vararray import EUDVArray
from ...localize import _


class _EUDStruct_Metaclass(type):
    def __init__(cls, name, bases, dct) -> None:
        # For field declaration, modify selftype to cls
        fielddict = {}
        fieldcount = 0
        for basetype in reversed(cls.__mro__):
            if not hasattr(basetype, "_fields_"):
                continue
            for i, nametype in enumerate(basetype._fields_):
                if isinstance(nametype, str):  # "fieldname"
                    fieldname = nametype
                    fieldtype = None
                else:  # ("fieldname", fieldtype)
                    fieldname = nametype[0]
                    fieldtype = nametype[1]
                if fieldtype is selftype:
                    fieldtype = cls
                    basetype._fields_[i] = (fieldname, cls)

                if fieldname in fielddict:
                    raise EPError(
                        _("Duplicated field name: {}").format(fieldname)
                    )
                fielddict[fieldname] = (fieldcount, fieldtype)
                fieldcount += 1

        cls._fielddict = fielddict
        super().__init__(name, bases, dct)

    def __mul__(self, times: int):
        basetype = self
        return _EUDStructArray(times, basetype)


class EUDStructArray(ExprProxy, metaclass=_EUDStruct_Metaclass):
    dontFlatten = True

    def __init__(self, initvar=None, *, _from=None, _times, _basetype):
        if _from is None:
            if initvar is None:
                initvals = [0] * _times
                super().__init__(EUDVArray(_times, _basetype)(initvals))
            else:
                super().__init__(EUDVArray(_times, _basetype)(initvar))
        else:
            super().__init__(EUDVArray(_times, _basetype).cast(_from))

        self._initialized = True
        self._times = _times

    def copy(self):
        """Create a shallow copy"""
        arraytype = type(self)
        inst = arraytype()
        self.copyTo(inst)
        return inst

    def copyTo(self, inst):
        """Copy struct to other instance"""
        for i in range(self._times):
            inst[i] = self[i]

    def __getitem__(self, index):
        return self.get_value()[index]

    def __setitem__(self, index, newval):
        self.get_value()[index] = newval

    def __getattr__(self, name):
        return super().__getattr__(name)

    def __setattr__(self, name, value):
        self.__dict__[name] = value


class _EUDStructArray:
    def __init__(self, times: int, basetype) -> None:
        self._times: int = times
        self._basetype = basetype

    def __call__(self, initvar=None, *, _from=None) -> EUDStructArray:
        return EUDStructArray(
            initvar=initvar,
            _from=_from,
            _times=self._times,
            _basetype=self._basetype,
        )

    def cast(self, _from):
        return self(_from=_from)
