from helper import *

N = 2000
arr = EUDArray(N)


@EUDFunc
def f_bubblesort():
    for i in EUDLoopRange(N):
        for j in EUDLoopRange(N - 1 - i):
            if EUDIf()(arr[i] >= arr[i + 1]):
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
            EUDEndIf()

    SetCurrentPlayer(P1)


@TestInstance
def test_perfbasic():
    f_srand(0)

    for i in EUDLoopRange(N):
        arr[i] = f_dwrand()

    test_perf("Bubble sort (%s)" % N, f_bubblesort, 1)
    test_perf("Basic looping (comparison)", lambda: None, 10000000)
