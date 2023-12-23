import time

import helper
import profile_tool

start_time = time.time()
DoCoverageTest = False

if DoCoverageTest:
    import coverage

    cov = coverage.Coverage()
    cov.start()


helper.EP_SetRValueStrictMode(True)

from unittests import (
    test_arithmetics,
    test_ctypes,
    test_dbstring,
    test_dict_typo,
    test_eps,
    test_fmtprint,
    test_locf,
    test_lvalue,
    test_once,
    test_parse,
    test_pexists,
    test_sq_from_1var,
    test_trace,
    test_unitgroup,
    testarray,
    testbinsearch,
    testbitwise,
    testblockstru,
    testcondition,
    testcpmemio,
    testcurpl,
    testdwmemio,
    testfptr,
    testlistloopcompiles,
    testmapdatahelper,
    testmath,
    testmultiret,
    testoperator,
    testpatch,
    testpool,
    testpoolfptr,
    testprint,
    testptrigger,
    testptrjump,
    testptrmemio,
    testpvariable,
    testshortcircuit,
    teststack,
    teststrfunc,
    teststruct,
    testswitch,
    testtypedf,
    testvarray,
    testvartrg,
    testxvartrg,
)

helper.CompressPayload(True)
helper.ShufflePayload(False)


def f():
    helper.test_runall("unittest")


from eudplib.eudlib.stringf.tblprint import _AddStatText


_AddStatText(open("unittests/custom_txt.tbl", "rb").read())


# profile_tool.profile(f, "profile.json")
f()
print("--- %s seconds ---" % (time.time() - start_time))

if DoCoverageTest:
    cov.stop()
    cov.html_report(include=["C:\\eudplib\\*"])
