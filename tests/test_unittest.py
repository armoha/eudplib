import time

import helper
import profile_tool

# ruff: noqa: I001
# fmt: off

start_time = time.time()
DoCoverageTest = False

if DoCoverageTest:
    import coverage

    cov = coverage.Coverage()
    cov.start()

# helper._use_ptr_array()
helper.EP_SetRValueStrictMode(True)

from unittests import (
    testblockstru,
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
    testshortcircuit,
    testlistloopcompiles,
    testmapdatahelper,
    test_trace,
    test_pexists,
    test_dbstring,
    test_ctypes,
    test_dict_typo,

    test_arithmetics,
    test_fmtprint,
    test_locf,
    test_once,
    test_parse,
    test_scdata,
    test_unitgroup,
    testcondition,
)
# fmt: on

helper.CompressPayload(True)
helper.ShufflePayload(False)


def f():
    helper.test_runall("unittest")


from eudplib.string.tblprint import _AddStatText


_AddStatText(open("unittests/custom_txt.tbl", "rb").read())


# profile_tool.profile(f, "profile.json")
f()
print("--- %s seconds ---" % (time.time() - start_time))

if DoCoverageTest:
    cov.stop()
    cov.html_report(include=["C:\\eudplib\\*"])
