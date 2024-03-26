#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


from abc import ABCMeta, abstractmethod

from typing_extensions import Self

from eudplib.localize import _

from .. import core as c
from .. import utils as ut


class SCDataObject(ut.ExprProxy, metaclass=ABCMeta):
    """
    SCDataObject class.
    SCDataObjects are object which are directly related to SC data.
    SCDataObject classes support manipulation of linked data
    via member get/set.
    """
    dont_flatten = True

    @abstractmethod
    def __init__(self, index) -> None:
        if isinstance(index, c.EUDVariable):
            new_index = c.EUDVariable()
            new_index << index
            index = new_index
        super().__init__(index)

    @classmethod
    def cast(cls: Self, _from) -> Self:
        try:
            return cls(_from)
        except TypeError as e:
            raise TypeError(_("Type {} is not castable").format(cls.__name__), e)

    def Evaluate(self):  # noqa: N802
        return c.Evaluate(self._value)

