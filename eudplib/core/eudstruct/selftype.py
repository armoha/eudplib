# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

_selftype = None


class selftype:  # noqa: N801
    """When used in EUDFuncMethod's type declaration, This is interpreted
    as the owning class itself
    """

    @staticmethod
    def cast(_from):
        return _selftype.cast(_from)


def _set_selftype(t):
    global _selftype
    _selftype = t
