from dataclasses import dataclass
from math import ceil, floor


@dataclass
class TriggerItem:
    name: str
    offset: int
    size: int = 1
    zeroed: bool = False


class EUDTrigger:
    def __init__(self, actno=1):
        assert 0 <= actno <= 64
        self.data = []
        item = lambda name, offset, size=1, **kwargs: self.data.append(
            TriggerItem(name, offset - 4, size, **kwargs)
        )
        item("nextptr", 4, 4)
        if 1 <= actno:
            item("nocond", 23, zeroed=True)
            item("condflag=0", 25, zeroed=True)
        k = 0
        for n in range(actno):
            item(f"a{n}mask=~0", 328 + k, 4)
            item(f"a{n}dest", 344 + k, 4)
            item(f"a{n}value", 348 + k, 4)
            item(f"a{n}unit=0", 352 + k, 2, zeroed=True)
            item(f"a{n}type=45", 354 + k)
            item(f"a{n}SetTo", 355 + k)
            item(f"a{n}flags", 356 + k)
            item(f"a{n}SC", 358 + k, 2)
            k += 32
        if 1 <= actno < 64:
            item("noact", 354 + k, zeroed=True)
            item("actflag=0", 356 + k, zeroed=True)
        if actno >= 0:
            item("flags", 2376)
            # item("currentAct", 2407, zeroed=True)

    def __str__(self):
        return str(self.data)


def stack(actno, size):
    count = 2408 // size + 1
    trigger = EUDTrigger(actno)
    byteset = set()
    zerobyte = set()
    t2 = [[] for _ in range(9632 // 4)]
    template = [[] for _ in range(size // 4)]
    template_start = int(ceil(2408 / size) * size)
    for n in range(count * 2):
        for data in trigger.data:
            for i in range(data.size):
                offset = data.offset + size * n + i
                if offset in byteset:  # and ("nextptr" in t2[offset // 4]):
                    if not (data.zeroed and offset in zerobyte):
                        return None
                byteset.add(offset)
                if data.zeroed:
                    zerobyte.add(offset)
                t2[offset // 4].append(data.name)
            if template_start <= offset < template_start + size:
                template[(offset - template_start) // 4].append(f"t{n}{data.name}")
    return template


for k in range(20, 36, 4):
    ret = stack(0, k)
    if ret:
        print(k, ret)
        break

lol = []
for n in range(2, 3):
    for size in range(32 * (n + 1), 2408, 4):
        ret = stack(n, size)
        if ret is None:
            continue
        print(f"> {n} action size: {size}, {100*72*n/size}%")
        # print(f"{size},", end=" ")
        lol.append(size)
        empty = []

        def flush(empty):
            # nonlocal empty
            if len(empty) >= 2:
                print(f"epd {empty[0]}~{empty[-1]} are empty")
            elif empty:
                print(f"epd {empty[0]} is empty")
            empty.clear()

        for i, dat in enumerate(ret):
            if dat:
                flush(empty)
                print(f"epd {i} : {dat}")
            else:
                empty.append(i)
        flush(empty)
        print("")
        break
