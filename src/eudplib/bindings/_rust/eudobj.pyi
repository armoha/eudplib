# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing_extensions import Self

from ...core.allocator.payload import ObjCollector
from .allocator import ConstExpr, ObjAllocator, PayloadBuffer, RlocInt_C

class EUDObject(ConstExpr):
    def __new__(cls) -> Self: ...
    def DynamicConstructed(self) -> bool: ...  # noqa: N802
    def Evaluate(self) -> RlocInt_C: ...  # noqa: N802
    def GetDataSize(self) -> int: ...  # noqa: N802
    def CollectDependency(self, pbuf: ObjCollector) -> None: ...  # noqa: N802
    def WritePayload(self, pbuf: ObjAllocator | PayloadBuffer) -> None: ...  # noqa: N802
