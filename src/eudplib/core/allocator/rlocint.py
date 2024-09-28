# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from ...bindings._rust import allocator as al

RlocInt_C = al.RlocInt_C
RlocInt = al.RlocInt
toRlocInt = al.toRlocInt  # noqa: N816
