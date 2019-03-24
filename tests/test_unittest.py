import profile_tool
import helper

DoCoverageTest = False

if DoCoverageTest:
    import coverage

    cov = coverage.Coverage()
    cov.start()


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
)

helper.CompressPayload(True)


def f():
    helper.PRT_SetPatchPassword('whatislove?')
    helper.test_runall("unittest")


# profile_tool.profile(f, 'profile.json')
f()

if DoCoverageTest:
    cov.stop()
    cov.html_report(include=["C:\\gitclones\\eudtrglib\\eudplib\\*"])
