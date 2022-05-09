#!/usr/bin/python
# -*- coding: utf-8 -*-

"""EUDBag type

- `Bag` in Artemis Framework
- Generalization of EUDVArray
- Fast to iterate, add and remove
- Fixed capacity, nextptr and destPlayer
- Unstable collection; removing item changes items' order
- Has length
"""

from .. import core as c
from ..utils import cachedfunc, ep_assert, ExprProxy


@cachedfunc
@cachedfunc
def EUDBag(size, basetype=None):
    ep_assert(isinstance(size, int) and 1 <= size <= 64)

    class _EUDBag(ExprProxy):
        def __init__(self, initvars=None, *, capacity, _from=None):
            # Initialization from value
            if _from is not None:
                if IsConstExpr(_from):
                    baseobj = _from

                # Initialization by variable reference
                else:
                    baseobj = EUDVariable()
                    baseobj << _from

            else:
                # Int -> interpret as sequence of 0s
                if initvars is None:
                    initvars = [(0,) * size] * size

                # For python iterables
                baseobj = EUDVArrayData(size)(initvars, dest=dest, nextptr=nextptr)

            super().__init__(baseobj)
            self.dontFlatten = True
            self._epd = EPD(self)
            self._basetype = basetype

        def __iter__(self):
            pass

    return _EUDBag
