from helper import *


@TestInstance
def test_ptrigger():
    if EUDPlayerLoop()():
        PTrigger(
            players=[Player1],
            actions=[
                SetDeaths(CurrentPlayer, Add, 1, "Terran Marine"),
                PreserveTrigger(),
            ],
        )

        PTrigger(
            players=[Player1, Player7],
            actions=[
                SetDeaths(CurrentPlayer, Add, 1, "Terran Marine"),
                PreserveTrigger(),
            ],
        )

        PTrigger(
            players=[Force1],
            actions=[
                SetDeaths(CurrentPlayer, Add, 1, "Terran Marine"),
                PreserveTrigger(),
            ],
        )
    EUDEndPlayerLoop()

    test_equality("PTrigger test", [f_dwread_epd(0), f_dwread_epd(6), f_dwread_epd(7)], [3, 1, 0])

    DoActions(SetDeaths(AllPlayers, SetTo, 0, "Terran Marine"))
