from helper import *


@TestInstance
def test_dbstring_from_string():
    from eudplib.string.dbstr import DBString

    a = DBString.cast("test")
    a.Display()
