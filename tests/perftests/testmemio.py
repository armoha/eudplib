from helper import *


cunitepd_old = f_readgen_epd(
    0x7FFFF8, (0, lambda x: x), (-0x58A364 // 4, lambda y: y // 4)
)


@TestInstance
def test_perfmemio():
    t = {}
    for i in range(1700):
        x = 0x59CCA8 + 336 * i
        try:
            t[bin(x).count("1")] = x
        except KeyError:
            continue
    c, ptr = EUDCreateVariables(2)
    v = EPD(c.getValueAddr())
    ptr << 0x58A364
    for i in range(5, 18 + 1):
        c << t[i]
        test_perf("cunitepd_old(bit%u)" % i, lambda: cunitepd_old(v), perf_basecount)
        test_perf(
            "epdcunit_new(bit%u)" % i, lambda: f_cunitepdread_epd(v), perf_basecount
        )
    c << 0
    test_perf("f_dwread_epd", lambda: f_dwread_epd(c), perf_basecount)
    test_perf("f_dwbreak", lambda: f_dwbreak(ptr), perf_basecount)
    test_perf("EPD", lambda: EPD(ptr), perf_basecount)
    test_perf("f_dwread", lambda: f_dwread(ptr), perf_basecount // 2)
    test_perf("f_wread", lambda: f_wread(ptr), perf_basecount // 2)
    test_perf("f_bread", lambda: f_bread(ptr), perf_basecount // 2)
