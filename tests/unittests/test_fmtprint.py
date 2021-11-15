from helper import *


@TestInstance
def test_fmtprint():
    name = EUDVariable(Db("dpdkfah"))
    amount = EUDVariable(336)
    resource = EUDArray([EPD(Db("minerals")), EPD(Db("gases"))])
    f_setcurpl(P1)
    f_eprintAll("{:s} gets {} {:t}.", name, amount, resource[0])
    errorline = 0x640B60 + 218 * 12

    expect = "dpdkfah\r gets \r\r336\r \r\r\rminerals.\r\r\r"
    expectdb = Db(expect)
    test_equality("f_eprintf test1", f_strlen(errorline), len(expect))
    test_equality("f_eprintf test2", f_memcmp(errorline, expectdb, len(expect)), 0)
