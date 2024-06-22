from helper import *


@TestInstance
def test_ptrjump():
    testvar = EUDVariable()
    a = EUDVariable()
    t = Forward()

    testvar += 1
    a << t
    testvar += 2
    EUDJump(t)
    testvar += 4
    t << NextTrigger()
    testvar += 8

    PushTriggerScope()
    end = Forward()
    trg = [
        RawTrigger(nextptr=end, actions=testvar.AddNumber(16 << i)) for i in range(4)
    ]
    PopTriggerScope()
    EUDJump(trg[1])
    with expect_eperror():
        EUDJump(trg[2])
    with expect_eperror():
        EUDJump(trg[3])
    end << NextTrigger()

    test_assert("Pointer jump test", testvar == 43)
