# TEST HELPER
import functools
import os as _os
import random as _random
import sys as _sys

_sys.path.insert(
    1, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
)


from eudplib import *
from eudplib.collections.eudarray import _use_ptr_array
from eudplib.eudlib.utilf.datadumper import _add_datadumper

_testFailed = EUDLightVariable()
_testNum = EUDVariable()
_failedNum = EUDVariable()


@functools.cache
def _failedTest():
    return EUDArray(1024)


###############################################################
# Unit testing helpers
###############################################################


origcp = EUDVariable()


def setcp1():
    origcp << f_getcurpl()
    f_setcurpl(Player1)


def resetcp():
    f_setcurpl(origcp)


def test_assert(testname, condition):
    global _failedNum, _testNum

    setcp1()

    if EUDIf()(condition):
        f_simpleprint("\x07 - [ OK ]\x04", testname)
        test_wait(0)
    if EUDElse()():
        f_simpleprint("\x08 - [FAIL]", testname)
        failedTestDb = Db(testname)
        _failedTest()[_failedNum] = failedTestDb
        _testFailed << 1
        test_wait(24)
    EUDEndIf()

    resetcp()

    _testNum += 1
    test_wait(0)


def test_equality(testname, real, expt):
    global _failedNum, _testNum

    real = Assignable2List(real)
    expt = Assignable2List(expt)
    assert len(real) == len(expt)

    setcp1()
    if EUDIf()([r == e for r, e in zip(real, expt)]):
        f_simpleprint("\x07 - [ OK ]\x04", testname)
        test_wait(0)
    if EUDElse()():
        f_simpleprint("\x08 - [FAIL]", testname)
        f_simpleprint(" \x03   - \x04 Output   : ", *real)
        f_simpleprint(" \x03   - \x04 Expected : ", *expt)
        failedTestDb = Db(testname)
        _failedTest()[_failedNum] = failedTestDb
        _failedNum += 1
        test_wait(24)
    EUDEndIf()

    resetcp()

    f_setcurpl(origcp)

    _testNum += 1


def test_operator(testname, realf, exptf=None):
    if exptf is None:
        exptf = realf

    try:
        f = realf._bodyfunc
    except AttributeError:
        f = realf
    argcount = f.__code__.co_argcount

    @TestInstance
    def test_operator():
        inputs = [EUDVariable() for _ in range(argcount)]
        expt, real = [], []

        for i in range(20):
            rnums = [_random.randint(0, 0xFFFFFFFF) for _ in range(argcount)]
            SetVariables(inputs, rnums)
            real.append(realf(*inputs))
            expt.append(exptf(*rnums) & 0xFFFFFFFF)

        test_assert(
            "Operator test : %s" % testname,
            [r == e for r, e in zip(real, expt)],
        )


class expect_error:
    def __init__(self, error):
        self._error = error

    def __enter__(self):
        PushTriggerScope()

    def __exit__(self, type, e, traceback):
        PopTriggerScope()
        if isinstance(e, self._error):
            print(f" - {self._error.__name__} as expected: {e}")
            return True
        else:
            raise RuntimeError(f"{self._error.__name__} not thrown")


class expect_eperror(expect_error):
    def __init__(self):
        super().__init__(EPError)


###############################################################
# Performance testing helper
###############################################################


perf_basecount = 200000


def test_perf(testname, func, count):
    starttm = f_dwread_epd(EPD(0x51CE8C))

    if EUDLoopN()(count):
        func()
    EUDEndLoopN()
    test_wait(0)

    endtm = f_dwread_epd(EPD(0x51CE8C))

    elapsedTime = starttm - endtm
    averageTime = elapsedTime // count
    setcp1()
    f_simpleprint(
        "\x03" * 150 + "[PERF] \x04%s \x03* %d    \x05" % (testname, count),
        averageTime,
        "/",
        elapsedTime,
        spaced=False,
    )
    resetcp()
    test_wait(12)


###############################################################


def test_complete():
    setcp1()
    f_simpleprint("\x03" + "=" * 40)
    succNum = _testNum - _failedNum
    f_simpleprint("\x04  Test result : ", succNum, "/", _testNum, spaced=False)
    resetcp()


_testList = []


def TestInstance(func):
    print(" - Adding test instance %s" % func.__name__)
    _testList.append((func, func.__name__))
    return func


@EUDFunc
def _testmain():
    for testfunc, testname in _testList:
        _testFailed << 0
        f_simpleprint("\x03[TEST] 테스트를 진행합니다:", testname)
        testfunc()
        test_equality(f"{testname} 종료", f_dwread_epd(0), 0)
        f_dwwrite_epd(0, 0)
        Trigger(_testFailed == 1, _failedNum.AddNumber(1))

    test_complete()


def test_runall(testname):
    LoadMap("outputmap/basemap/basemap_strx.scx")
    SaveMap("outputmap/test_%s.scx" % testname, _testmain)
    print(f"eudplib version {eudplibVersion()}")


def test_wait(time):
    DoActions(SetMemory(0x6509A0, SetTo, time))
    EUDDoEvents()
