from helper import *


@TestInstance
def test_strbuffer():
    origcp = f_getcurpl()

    s1 = StringBuffer(1023)

    a = EUDVariable(4006547881)
    s1.insert(0, a)

    b = EUDVariable(0xB91083F5)
    s1.append(hptr(b))

    s1.append(347, "test.")
    EP_SetRValueStrictMode(False)
    s1.delete(1, 1)
    EP_SetRValueStrictMode(True)

    userid = f_getuserplayerid()
    DoActions(SetCurrentPlayer(userid), SetMemory(0x640B58, SetTo, 0))
    s1.Display()

    test_assert(
        "StringBuffer test",
        [
            Memory(0x640B60, Exactly, b2i4(b"4006")),
            Memory(0x640B64, Exactly, b2i4(b"\r\r\r\r")),
            Memory(0x640B68, Exactly, b2i4(b"81\r\r")),
            Memory(0x640B6C, Exactly, b2i4(b"B910")),
            Memory(0x640B70, Exactly, b2i4(b"83F5")),
            Memory(0x640B74, Exactly, b2i4(b"347\r")),
            Memory(0x640B78, Exactly, b2i4(b"test")),
            Memory(0x640B7C, Exactly, b2i4(b".\r\r\r")),
            MemoryX(0x640B80, Exactly, 0, 0xFF),
        ],
    )

    s2 = StringBuffer(1023)
    s2Addr = GetMapStringAddr(s2.StringIndex)

    test_assert(
        "StringBuffer uniqueness test",
        [s1.StringIndex != s2.StringIndex, GetMapStringAddr(s1.StringIndex) != s2Addr],
    )

    f_dwwrite(0x640B58, 6)
    s2.print(PName(userid), "님 안녕하세요")
    username = 0x57EEEB + 36 * userid
    unamelen = f_strlen(username)

    test_equality(
        "PName test",
        [
            f_memcmp(s2Addr, username, unamelen),
            f_memcmp(0x640B60 + 218 * 6, username, unamelen),
        ],
        [0, 0],
    )

    cmp_db = Db("SetPNameTest:\x07 테스트입니다.\r\r")  # 36
    f_dbstr_print(0x64107C, ptr2s(username), u2utf8(":\x07 테스트입니다."))
    SetPName(userid, "SetPNameTest")
    test_equality("SetPName test", f_memcmp(0x64107C, cmp_db, 40), 0)

    name_db = Db(25)
    name_var = EUDVariable(name_db)
    f_dbstr_print(name_db, ptr2s(username))
    ret = EUDVariable(0)

    RawTrigger(
        conditions=IsPName(P1, "Armo"),
        actions=ret.AddNumber(1),
    )
    RawTrigger(
        conditions=IsPName(P1, "trgk"),
        actions=ret.AddNumber(16),
    )
    test_equality("IsPName test1", ret, 0b1)

    Trigger(
        conditions=IsPName(userid, "Armo"),
        actions=ret.AddNumber(2),
    )
    Trigger(
        conditions=IsPName(userid, "trgk"),
        actions=ret.AddNumber(16),
    )
    test_equality("IsPName test2", ret, 0b11)

    Trigger(
        conditions=IsPName(P1, name_var),
        actions=ret.AddNumber(4),
    )
    Trigger(
        conditions=IsPName(P1, Db("trgk")),
        actions=ret.AddNumber(16),
    )
    test_equality("IsPName test3", ret, 0b111)

    Trigger(
        conditions=IsPName(userid, name_var),
        actions=ret.AddNumber(8),
    )
    Trigger(
        conditions=IsPName(userid, EUDVariable(Db("trgk"))),
        actions=ret.AddNumber(16),
    )
    test_equality("IsPName test4", ret, 0b1111)

    s2.fadeIn("abc", line=10)
    s2.fadeIn("abc", line=EUDVariable(-1))
    s2.fadeOut("abc", line=10)
    s2.fadeOut("abc", line=EUDVariable(-1))
    s2.tagprint("dpdkfah")
    s2.tagprint("dpdkfah", line=EUDVariable(-1))
    SetPName(userid, "TestPName{:c}{:n}", userid, userid)
    SetPName(P1, "TestTest")
    SetPName(P2, "TestTest")
    SetPName(P4, "TestTest")
    SetPNamef(userid, "SetPNameTest{}", userid)

    f_setcurpl(origcp)
