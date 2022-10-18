import random

i32 = lambda: random.randint(1, 0xFFFFFFFF)
shift = lambda: random.randint(0, 31)

test_write_values = (
    [i32() for _ in range(6)] + [shift() for _ in range(2)] + [i32() for _ in range(3)]
)


def GetValues():
    return test_write_values.copy()
