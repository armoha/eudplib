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
from ..utils import ep_assert


class EUDBag:
    def __init__(self, capacity):
        self.capacity = capacity
        self.loopvar = {}
        self.cpvar = None
        self.non_default = []
        self.default = []
        self.keyword_only = []
        args = vars(self.__class__)
        self.loopvar = {name: EUDVariable() for name in args if not name.startswith("__")}
        for name, initval in args:
            # ignore python system attributes
            if name.startswith("__"):
                continue
            # CP trick member
            if initval is c.CurrentPlayer:
                ep_assert(self.cpvar is None, f"Multiple CurrentPlayer members are disallowed: {self.cpvar} and {name}")
                self.cpvar = name
                self.loopvar[name]._vartrigger._initval = (0xFFFFFFFF, c.EncodePlayer(c.CurrentPlayer), 0, 0x072D0000, 0)
            # positional args
            if initval in (None, c.CurrentPlayer):
                if self.default:
                    self.keyword_only.append((name, None))
                else:
                    self.non_default.append(name)
            elif self.keyword_only:
                self.keyword_only.append((name, initval))
            else:
                self.default.append((name, initval))

    def add(self, *args, **kwargs):
        if len(args) > len(self.non_default) + len(self.default):
            raise TypeError(f"{self.__class__.__name__}.add takes from {len(self.non_default)} to {len(self.non_default) + len(self.default)} positional arguments but {len(args)} were given")
        if len(args) < len(self.non_default):
            missing_args = []
            for arg in self.non_default[len(args):]:
                if arg not in kwargs:
                    missing_args.append(arg)
            if missing_args:
                raise TypeError(f"{self.__class__.__name__}.add missing {len(missing_args)} required positional arguments: {*missing_args}")
        for arg in self.non_default[:len(args)]:
            if arg in kwargs:
                raise TypeError(f"{self.__class__.__name__}.add got multiple values for argument {arg}")
        if self.keyword_only:
            missing_kwargs = []
            for kwarg in self.keyword_only:
                if kwarg not in kwargs:
                missing_kwargs.append(kwarg)
            if missing_kwargs:
                raise TypeError(f"{self.__class__.__name__}.add missing {len(missing_kwargs)} required positional arguments: {*missing_kwargs}")

    def __iter__(self):
        pass
