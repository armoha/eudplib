# Test for complex map

import os
import sys

sys.path.insert(0, os.path.abspath("..\\"))

from eudplib import *

"""
Creep reading
"""

mapwidth, mapheight, creepaddr_epd = EUDCreateVariables(3)


@EUDFunc
def f_creepread_init():
    # Get creepmap address
    creepaddr_epd << f_epdread_epd(EPD(0x6D0E84))
    SetVariables([mapwidth, mapheight], f_dwbreak(f_dwread_epd(EPD(0x57F1D4)))[0:2])


@EUDFunc
def f_creepread(x, y):
    ret = EUDCreateVariables(1)

    creepindex = mapwidth * y + x
    creepdwordindex, creepevenodd = f_div(creepindex, 2)

    # read tile data
    creepdat_epd = creepaddr_epd + creepdwordindex
    creepdat_word0, creepdat_word1 = f_dwbreak(f_dwread_epd(creepdat_epd))[0:2]

    # select word0/word1 by evenodd
    if EUDIf()(creepevenodd == 0):
        ret << creepdat_word0

    if EUDElse()():
        ret << creepdat_word1

    EUDEndIf()

    return ret


"""
Main logic
"""

LoadMap("outputmap/basemap/creeptest_basemap.scx")
# CompressPayload(True)


@EUDFunc
def main():
    # Iterate through each units.
    unitptr, unitepd = EUDCreateVariables(2)

    f_creepread_init()

    # Turbo rawtrigger

    if EUDWhile()(Always()):
        DoActions(SetDeaths(203151, SetTo, 1, 0))
        f_setcurpl(0)

        # Loop for every units
        for unitptr, unitepd in EUDLoopUnit():
            # check unittype
            # /*0x064*/ u16         unitType;
            unittype = f_dwbreak(f_dwread_epd(unitepd + (0x64 // 4)))[0]
            EUDContinueIfNot(unittype == EncodeUnit("Zerg Zergling"))

            # Get x, y coordinates of this unit.
            # uint16 unitx : unit + 0x28
            # uint16 unity : unit + 0x2A
            coord = f_dwread_epd(unitepd + (0x28 // 4))
            unitx, unity = f_dwbreak(coord)[0:2]

            # Convert coordinates to tile coordinates
            tileunitx = unitx // 32
            tileunity = unity // 32

            # creep -> continue
            creepval = f_creepread(tileunitx, tileunity)
            EUDContinueIf([creepval >= 16, creepval <= 31])

            # Slow down zergling.
            # Creating kakaru and killing them slows down zergling.
            SeqCompute(
                [
                    (EPD(0x58DC60 + 0), SetTo, unitx),
                    (EPD(0x58DC60 + 4), SetTo, unity),
                    (EPD(0x58DC60 + 8), SetTo, unitx),
                    (EPD(0x58DC60 + 12), SetTo, unity),
                ]
            )

            DoActions(
                CreateUnit(1, "Kakaru (Twilight Critter)", 1, Player1),
                RemoveUnitAt(All, "Kakaru (Twilight Critter)", 1, Player1),
            )

        DoActions(KillUnit("Kakaru (Twilight Critter)", Player1))

        EUDDoEvents()

    EUDEndWhile()


SaveMap("outputmap/testcreep.scx", main)
