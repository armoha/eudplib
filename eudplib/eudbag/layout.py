from dataclasses import dataclass
import enum

# fmt: off
# See https://github.com/armoha/euddraft/discussions/60
_overlap_distance = (
      20,
      72,  104,  152,  160,  260,  260,  292,  292,
     616,  648,  680,  708,  740,  772,  812,  844,
     876,  908,  940,  972, 1004, 1028, 1060, 1092,
    1124, 1156, 1204, 1236, 1268, 1300, 1332, 1364,
    1396, 1428, 1460, 1492, 1524, 1556, 1588, 1620,
    1652, 1684, 1716, 1748, 1780, 1812, 1844, 1876,
    1908, 1940, 1972, 2004, 2036, 2052, 2084, 2116,
    2148, 2180, 2212, 2244, 2276, 2308, 2340, 2376,
)
# fmt: on


class TrgItem(enum.Enum):
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__) + 1
        return obj

    def __init__(self, size: int) -> None:
        self.size = size

    NEXT_PTR = 4
    NO_COND = 1
    BIT_MASK = 4
    DEST_VAL_UNIT_ACTTYPE_MOD_ACTFLAG_SC = 16
    NO_ACT = 1
    TRGFLAG = 1


class Space:
    def __init__(self, size: int) -> None:
        self.size = size


layouts: tuple[tuple[TrgItem | Space, ...], ...] = (
    (
        TrgItem.NEXT_PTR,
        Space(6),
        TrgItem.NO_ACT,
        Space(1),
        TrgItem.TRGFLAG,
        Space(6),
        TrgItem.NO_COND,
    ),
    (
        TrgItem.BIT_MASK,
        Space(12),
        TrgItem.DEST_VAL_UNIT_ACTTYPE_MOD_ACTFLAG_SC,
        TrgItem.TRGFLAG,
        Space(3),
        TrgItem.NEXT_PTR,
        Space(15),
        TrgItem.NO_COND,
        Space(2),
        TrgItem.NO_ACT,
        Space(13),
    ),
)


if __name__ == "__main__":
    for n, layout in enumerate(layouts):
        overlap_size = _overlap_distance[n]
        size = sum(item.size for item in layout)
        assert overlap_size == size, f"{n} act size mismatch: {overlap_size} != {size}"
