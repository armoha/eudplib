import profile_tool
import helper
import time

start_time = time.time()
DoCoverageTest = False

if DoCoverageTest:
    import coverage

    cov = coverage.Coverage()
    cov.start()


helper.EP_SetRValueStrictMode(True)

from unittests import (
    testblockstru,
    testcondition,
    testcurpl,
    testpatch,
    testarray,
    testptrigger,
    testoperator,
    testptrjump,
    testfptr,
    testprint,
    testswitch,
    testvartrg,
    testxvartrg,
    testmultiret,
    testvarray,
    testpvariable,
    teststruct,
    teststrfunc,
    testmath,
    testbinsearch,
    testbitwise,
    teststack,
    testdwmemio,
    testcpmemio,
    testptrmemio,
    testtypedf,
    testpool,
    testpoolfptr,
    test_lvalue,
    test_sq_from_1var,
    test_eps,
    test_once,
    testshortcircuit,
    testlistloopcompiles,
    testmapdatahelper,
    test_trace,
    test_pexists,
    test_dbstring,
    test_ctypes,
    test_dict_typo,
    test_locf,
    test_fmtprint,
    test_parse,
    test_arithmetics,
)

helper.CompressPayload(True)
helper.ShufflePayload(False)


def f():
    helper.test_runall("unittest")


# profile_tool.profile(f, "profile.json")
f()
print("--- %s seconds ---" % (time.time() - start_time))

if DoCoverageTest:
    cov.stop()
    cov.html_report(include=["C:\\gitclones\\eudtrglib\\eudplib\\*"])
