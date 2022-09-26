from helper import *


@EUDFunc
def callonly():
    pass


def empty():
    pass


@TestInstance
def test_perfbasic():
    test_perf("Basic looping", lambda: None, 100 * perf_basecount)
    test_perf("Basic function call", EUDFunc(lambda: None), 100 * perf_basecount)

    a, b = EUDCreateVariables(2)
    SetVariables([a, b], [f_dwrand(), f_rand()])

    # Comparison of various functions
    test_perf("Addition", lambda: a + b, perf_basecount)
    test_perf("Subtraction", lambda: a - b, perf_basecount)
    test_perf("Multiplication", lambda: a * b, perf_basecount)
    test_perf("Division", lambda: a // b, perf_basecount)
