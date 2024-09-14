# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import TypeAlias

from eudplib.bindings._rust import allocator as al

from ...utils import ExprProxy
from .rlocint import RlocInt_C

ConstExpr = al.ConstExpr
Forward = al.Forward
Evaluable: TypeAlias = ConstExpr | int | ExprProxy[ConstExpr] | RlocInt_C
Evaluate = al.Evaluate
IsConstExpr = al.IsConstExpr
