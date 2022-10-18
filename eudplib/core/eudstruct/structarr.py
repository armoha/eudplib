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

from ...utils import ExprProxy
from .selftype import selftype
from .vararray import EUDVArray


class _EUDStruct_Metaclass(type):
    def __init__(cls, name, bases, dct):
        # For field declaration, modify selftype to cls
        try:
            fields = dct["_fields_"]
            for i in range(len(fields)):
                member = fields[i]

                if isinstance(member, str):
                    continue
                mName, mType = member
                if mType is selftype:
                    fields[i] = (mName, cls)
        except KeyError as e:
            pass

        super().__init__(name, bases, dct)

    def __mul__(self, times):
        basetype = self

        class EUDStructArray(ExprProxy):
            __metaclass__ = _EUDStruct_Metaclass

            def __init__(self, initvar=None, *, _from=None):
                if _from is None:
                    if initvar is None:
                        initvals = [0 for _ in range(times)]
                        super().__init__(EUDVArray(times, basetype)(initvals))
                    else:
                        super().__init__(EUDVArray(times, basetype)(initvar))
                else:
                    super().__init__(EUDVArray(times, basetype).cast(_from))

                self._initialized = True
                self.dontFlatten = True

            def copy(self):
                """Create a shallow copy"""
                arraytype = type(self)
                inst = arraytype()
                self.copyTo(inst)
                return inst

            def copyTo(self, inst):
                """Copy struct to other instance"""
                for i in range(times):
                    inst[i] = self[i]

            def __getitem__(self, index):
                return self.getValue()[index]

            def __setitem__(self, index, newval):
                self.getValue()[index] = newval

            def __getattr__(self, name):
                return super().__getattr__(name)

            def __setattr__(self, name, value):
                self.__dict__[name] = value

        return EUDStructArray
