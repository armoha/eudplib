## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY
from eudplib import *
from eudplib.core.eudfunc import EUDTraceLog, EUDTracedFunc, EUDTracedTypedFunc, EUDTracedMethod, EUDTracedTypedMethod
from eudplib.epscript.helper import _RELIMP, _TYGV, _TYSV, _TYLV, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LSH, _ALL
# (Line 1) import .relimpCycle1;
# (Line 3) function updateUnitNameAndRank() {
try:
    relimpCycle1 = _RELIMP(".", "relimpCycle1")
except ImportError:
    from . import relimpCycle1
@EUDFunc
def f_updateUnitNameAndRank():
    # (Line 5) const NAME_STR = EncodeString(py_eval("99 * '\\r'"));
    NAME_STR = EncodeString(eval("99 * '\\r'"))
    # (Line 8) const RANK_TBL = $B("Recruit (Rank)");
    RANK_TBL = EncodeTBL("Recruit (Rank)")
    # (Line 10) const LOCAL_UNIT_SELECT = EPD(0x6284B8);  // 선택한 유닛 (비공유)
    LOCAL_UNIT_SELECT = EPD(0x6284B8)
    # (Line 11) /* TEST */ dwwrite_epd(LOCAL_UNIT_SELECT, 0x59CCA8 + 336);
    f_dwwrite_epd(LOCAL_UNIT_SELECT, 0x59CCA8 + 336)
    # (Line 12) static var selectedUnitPtr, selectedUnitEpd = 0, 0;
    selectedUnitPtr, selectedUnitEpd = _TYSV([None, None], [0, 0])
    # (Line 13) if (!MemoryEPD(LOCAL_UNIT_SELECT, Exactly, selectedUnitPtr)) {
    if EUDIf()(MemoryEPD(LOCAL_UNIT_SELECT, Exactly, selectedUnitPtr), neg=True):
        # (Line 14) selectedUnitPtr, selectedUnitEpd = cunitepdread_epd(LOCAL_UNIT_SELECT);
        _SV([selectedUnitPtr, selectedUnitEpd], [f_cunitepdread_epd(LOCAL_UNIT_SELECT)])
        # (Line 15) }
        # (Line 16) if (selectedUnitPtr == 0) return -1, -1;
    EUDEndIf()
    if EUDIf()(selectedUnitPtr == 0):
        EUDReturn(-1, -1)
        # (Line 17) /* TEST */ dwwrite_epd(LOCAL_UNIT_SELECT, 0);
    EUDEndIf()
    f_dwwrite_epd(LOCAL_UNIT_SELECT, 0)
    # (Line 18) const namePtr = GetMapStringAddr(NAME_STR);
    namePtr = GetMapStringAddr(NAME_STR)
    # (Line 19) var rankPtr;
    rankPtr = EUDVariable()
    # (Line 20) once rankPtr = GetTBLAddr(RANK_TBL);
    _t3 = EUDExecuteOnce()
    if _t3():
        rankPtr << (GetTBLAddr(RANK_TBL))
        # (Line 21) const unitTypes = py_list();
    EUDEndExecuteOnce()
    unitTypes = list()
    # (Line 22) const unit = CUnit(selectedUnitEpd, ptr=selectedUnitPtr);
    unit = CUnit(selectedUnitEpd, ptr=selectedUnitPtr)
    # (Line 24) const Ticket = EUDArray(py_range(8));
    Ticket = EUDArray(range(8))
    # (Line 25) const Ore = EUDArray(py_range(1, 17, 2));
    Ore = EUDArray(range(1, 17, 2))
    # (Line 26) const Gas = EUDArray(py_range(2, 26, 3));
    Gas = EUDArray(range(2, 26, 3))
    # (Line 28) /* TEST */ dwwrite(0x59CCA8 + 336 + 0x64, $U("Terran Academy"));
    f_dwwrite(0x59CCA8 + 336 + 0x64, EncodeUnit("Terran Academy"))
    # (Line 29) /* TEST */ bwrite(0x59CCA8 + 336 + 0x4C, $P2);
    f_bwrite(0x59CCA8 + 336 + 0x4C, 1)
    # (Line 31) epdswitch (unit + 0x64/4, 255) {
    EPDSwitch(unit + 0x64 // 4, 255)
    # (Line 32) case $U("Terran Academy"):
    _t4 = EUDSwitchCase()
    # (Line 33) sprintf(namePtr, "Ticket {}, Ore {}, Gas {}", Ticket[unit.owner], Ore[unit.owner], Gas[unit.owner]);
    if _t4(EncodeUnit("Terran Academy")):
        f_sprintf(namePtr, "Ticket {}, Ore {}, Gas {}", Ticket[unit.owner], Ore[unit.owner], Gas[unit.owner])
        # (Line 34) sprintf(rankPtr, "{}", unit.unitType);
        f_sprintf(rankPtr, "{}", unit.unitType)
        # (Line 35) break;
        EUDBreak()
        # (Line 36) unitTypes.extend((EUDGetLastBlockOfName("swblock"))[1][py_str("casebrlist")].keys());
        unitTypes.extend((EUDGetLastBlockOfName("swblock"))[1][str("casebrlist")].keys())
        # (Line 37) }
    # (Line 38) once {
    EUDEndSwitch()
    _t5 = EUDExecuteOnce()
    if _t5():
        # (Line 39) const actions = py_list();
        actions = list()
        # (Line 40) foreach(unitType : unitTypes) {
        for unitType in unitTypes:
            # (Line 41) actions.append(SetMemoryX(
            # (Line 42) 0x660260 + 2 * unitType,
            # (Line 43) SetTo,
            # (Line 44) NAME_STR << (16 * (unitType % 2)),
            # (Line 45) 0xFFFF << (16 * (unitType % 2))
            # (Line 46) ));
            actions.append(SetMemoryX(0x660260 + 2 * unitType, SetTo, _LSH(NAME_STR,(16 * (unitType % 2))), _LSH(0xFFFF,(16 * (unitType % 2)))))
            # (Line 47) }
            # (Line 48) DoActions(actions);

        DoActions(actions)
        # (Line 49) }
        # (Line 51) setcurpl(getuserplayerid());
    EUDEndExecuteOnce()
    f_setcurpl(f_getuserplayerid())
    # (Line 52) DisplayText(NAME_STR);
    # (Line 53) const tests = "Ticket 1, Ore 3, Gas 5", "{}".format($U("Terran Academy"));
    DoActions(DisplayText(NAME_STR))
    tests = "Ticket 1, Ore 3, Gas 5", "{}".format(EncodeUnit("Terran Academy"))
    # (Line 54) return memcmp(namePtr, Db(tests[0]), py_len(tests[0].encode("utf-8")) + 1),
    # (Line 55) memcmp(rankPtr, Db(tests[1]), py_len(tests[1].encode("utf-8")) + 1);
    EUDReturn(f_memcmp(namePtr, Db(tests[0]), len(tests[0].encode("utf-8")) + 1), f_memcmp(rankPtr, Db(tests[1]), len(tests[1].encode("utf-8")) + 1))
    # (Line 56) }
