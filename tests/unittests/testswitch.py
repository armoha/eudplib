from random import sample, shuffle

from helper import *


@TestInstance
def main():
    i = EUDVariable()
    s = EUDVariable()

    if EUDWhile()(i <= 11 - 1):
        i += 1

        EUDSwitch(i)
        if EUDSwitchCase()(7):
            s += 1

        if EUDSwitchCase()(3):
            s += 10

        if EUDSwitchCase()(4, 6):
            s += 100
            EUDBreak()

        if EUDSwitchCase()(1, 2, 5, 8):
            s += 1000
            EUDBreak()

        # negative number is allowed only with full-ranged mask
        if EUDSwitchCase()(-1, -3, -7):
            s += -666
            EUDBreak()

        if EUDSwitchDefault()():
            s += 10000

        EUDEndSwitch()
    EUDEndWhile()
    test_equality("Switch test", s, 34421)

    random_numbers = sample(range(8192), 32)
    random_cases = random_numbers[:16]

    @EUDFunc
    def branch(x):
        ret = EUDVariable()
        ret << 0
        EUDSwitch(x, 8191)
        for case in random_cases:
            if EUDSwitchCase()(case):
                ret << 3 * case
                EUDBreak()
        if EUDSwitchDefault()():
            ret << -1
        EUDEndSwitch()
        return ret

    shuffle(random_numbers)
    ra = EUDArray(random_numbers)
    SetVariables([s, i], [0, 0])
    if EUDWhileNot()(i >= 32):
        x = branch(ra[i])
        SetVariables([i, s], [1, x], [Add, Add])
    EUDEndWhile()

    result = (-16 + 3 * sum(random_cases)) & 0xFFFFFFFF

    test_equality("Switch binary search test", s, result)
