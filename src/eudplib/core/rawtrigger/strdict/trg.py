# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from typing import Literal, TypeAlias

DefLocationDict: dict[str, int] = {
    "Location %u" % i: i for i in range(1, 256) if i != 64
}
DefLocationDict["Anywhere"] = 64

DefSwitchDict: dict[str, int] = {"Switch %d" % (i + 1): i for i in range(256)}

# ======================================

DefUnitDict: dict[str, int] = {
    "Terran Marine": 0,
    "Terran Ghost": 1,
    "Terran Vulture": 2,
    "Terran Goliath": 3,
    "Goliath Turret": 4,
    "Terran Siege Tank (Tank Mode)": 5,
    "Siege Tank Turret (Tank Mode)": 6,
    "Tank Turret type   1": 6,
    "Terran SCV": 7,
    "Terran Wraith": 8,
    "Terran Science Vessel": 9,
    "Gui Montag": 10,
    "Gui Montag (Firebat)": 10,
    "Terran Dropship": 11,
    "Terran Battlecruiser": 12,
    "Spider Mine": 13,
    "Vulture Spider Mine": 13,
    "Nuclear Missile": 14,
    "Terran Civilian": 15,
    "Sarah Kerrigan": 16,
    "Sarah Kerrigan (Ghost)": 16,
    "Alan Schezar": 17,
    "Alan Schezar (Goliath)": 17,
    "Alan Schezar Turret": 18,
    "Alan Turret": 18,
    "Jim Raynor (Vulture)": 19,
    "Jim Raynor (Marine)": 20,
    "Tom Kazansky": 21,
    "Tom Kazansky (Wraith)": 21,
    "Magellan": 22,
    "Magellan (Science Vessel)": 22,
    "Edmund Duke (Tank Mode)": 23,
    "Edmund Duke Turret (Tank Mode)": 24,
    "Duke Turret type   1": 24,
    "Edmund Duke (Siege Mode)": 25,
    "Edmund Duke Turret (Siege Mode)": 26,
    "Duke Turret type   2": 26,
    "Arcturus Mengsk": 27,
    "Arcturus Mengsk (Battlecruiser)": 27,
    "Hyperion": 28,
    "Hyperion (Battlecruiser)": 28,
    "Norad II (Battlecruiser)": 29,
    "Terran Siege Tank (Siege Mode)": 30,
    "Siege Tank Turret (Siege Mode)": 31,
    "Tank Turret type   2": 31,
    "Terran Firebat": 32,
    "Scanner Sweep": 33,
    "Terran Medic": 34,
    "Zerg Larva": 35,
    "Zerg Egg": 36,
    "Zerg Zergling": 37,
    "Zerg Hydralisk": 38,
    "Zerg Ultralisk": 39,
    "Zerg Broodling": 40,
    "Zerg Drone": 41,
    "Zerg Overlord": 42,
    "Zerg Mutalisk": 43,
    "Zerg Guardian": 44,
    "Zerg Queen": 45,
    "Zerg Defiler": 46,
    "Zerg Scourge": 47,
    "Torrasque": 48,
    "Torrasque (Ultralisk)": 48,
    "Matriarch": 49,
    "Matriarch (Queen)": 49,
    "Infested Terran": 50,
    "Infested Kerrigan": 51,
    "Infested Kerrigan (Infested Terran)": 51,
    "Unclean One": 52,
    "Unclean One (Defiler)": 52,
    "Hunter Killer": 53,
    "Hunter Killer (Hydralisk)": 53,
    "Devouring One": 54,
    "Devouring One (Zergling)": 54,
    "Kukulza (Mutalisk)": 55,
    "Kukulza (Guardian)": 56,
    "Yggdrasill": 57,
    "Yggdrasill (Overlord)": 57,
    "Terran Valkyrie": 58,
    "Mutalisk Cocoon": 59,
    "Cocoon": 59,
    "Protoss Corsair": 60,
    "Protoss Dark Templar": 61,
    "Protoss Dark Templar (Unit)": 61,
    "Zerg Devourer": 62,
    "Protoss Dark Archon": 63,
    "Protoss Probe": 64,
    "Protoss Zealot": 65,
    "Protoss Dragoon": 66,
    "Protoss High Templar": 67,
    "Protoss Archon": 68,
    "Protoss Shuttle": 69,
    "Protoss Scout": 70,
    "Protoss Arbiter": 71,
    "Protoss Carrier": 72,
    "Protoss Interceptor": 73,
    "Dark Templar": 74,
    "Dark Templar (Hero)": 74,
    "Protoss Dark Templar (Hero)": 74,
    "Zeratul": 75,
    "Zeratul (Dark Templar)": 75,
    "Tassadar/Zeratul": 76,
    "Tassadar/Zeratul (Archon)": 76,
    "Fenix (Zealot)": 77,
    "Fenix (Dragoon)": 78,
    "Tassadar": 79,
    "Tassadar (Templar)": 79,
    "Mojo": 80,
    "Mojo (Scout)": 80,
    "Warbringer": 81,
    "Warbringer (Reaver)": 81,
    "Gantrithor": 82,
    "Gantrithor (Carrier)": 82,
    "Protoss Reaver": 83,
    "Protoss Observer": 84,
    "Protoss Scarab": 85,
    "Danimoth": 86,
    "Danimoth (Arbiter)": 86,
    "Aldaris": 87,
    "Aldaris (Templar)": 87,
    "Artanis": 88,
    "Artanis (Scout)": 88,
    "Rhynadon": 89,
    "Rhynadon (Badlands)": 89,
    "Rhynadon (Badlands Critter)": 89,
    "Bengalaas": 90,
    "Bengalaas (Jungle)": 90,
    "Bengalaas (Jungle Critter)": 90,
    "Cargo Ship": 91,
    "Cargo Ship (Unused)": 91,
    "Unused type   1": 91,
    "Unused type   2": 92,
    "Mercenary Gunship": 92,
    "Mercenary Gunship (Unused)": 92,
    "Scantid": 93,
    "Scantid (Desert)": 93,
    "Scantid (Desert Critter)": 93,
    "Kakaru": 94,
    "Kakaru (Twilight)": 94,
    "Kakaru (Twilight Critter)": 94,
    "Ragnasaur": 95,
    "Ragnasaur (Ashworld)": 95,
    "Ragnasaur (Ashworld Critter)": 95,
    "Ursadon": 96,
    "Ursadon (Ice World)": 96,
    "Ursadon (Ice World Critter)": 96,
    "Lurker Egg": 97,
    "Zerg Lurker Egg": 97,
    "Raszagal": 98,
    "Raszagal (Corsair)": 98,
    "Samir Duran": 99,
    "Samir Duran (Ghost)": 99,
    "Alexei Stukov": 100,
    "Alexei Stukov (Ghost)": 100,
    "Map Revealer": 101,
    "Gerard DuGalle": 102,
    "Gerard DuGalle (Ghost)": 102,
    "Gerard DuGalle (BattleCruiser)": 102,
    "Zerg Lurker": 103,
    "Infested Duran": 104,
    "Infested Duran (Infested Terran)": 104,
    "Disruption Web": 105,
    "Disruption Field": 105,
    "Terran Command Center": 106,
    "Terran Comsat Station": 107,
    "Terran Nuclear Silo": 108,
    "Terran Supply Depot": 109,
    "Terran Refinery": 110,
    "Terran Barracks": 111,
    "Terran Academy": 112,
    "Terran Factory": 113,
    "Terran Starport": 114,
    "Terran Control Tower": 115,
    "Terran Science Facility": 116,
    "Terran Covert Ops": 117,
    "Terran Physics Lab": 118,
    "Starbase": 119,
    "Starbase (Unused)": 119,
    "Unused Terran Bldg type   1": 119,
    "Terran Machine Shop": 120,
    "Repair Bay": 121,
    "Repair Bay (Unused)": 121,
    "Unused Terran Bldg type   2": 121,
    "Terran Engineering Bay": 122,
    "Terran Armory": 123,
    "Terran Missile Turret": 124,
    "Terran Bunker": 125,
    "Norad II (Crashed)": 126,
    "Norad II (Crashed Battlecruiser)": 126,
    "Ion Cannon": 127,
    "Uraj Crystal": 128,
    "Khalis Crystal": 129,
    "Infested Command Center": 130,
    "Zerg Hatchery": 131,
    "Zerg Lair": 132,
    "Zerg Hive": 133,
    "Zerg Nydus Canal": 134,
    "Zerg Hydralisk Den": 135,
    "Zerg Defiler Mound": 136,
    "Zerg Greater Spire": 137,
    "Zerg Queen's Nest": 138,
    "Zerg Evolution Chamber": 139,
    "Zerg Ultralisk Cavern": 140,
    "Zerg Spire": 141,
    "Zerg Spawning Pool": 142,
    "Zerg Creep Colony": 143,
    "Zerg Spore Colony": 144,
    "Unused Zerg Bldg": 145,
    "Unused Zerg Building1": 145,
    "Zerg Sunken Colony": 146,
    "Zerg Overmind (With Shell)": 147,
    "Zerg Overmind": 148,
    "Zerg Extractor": 149,
    "Mature Chrysalis": 150,
    "Zerg Cerebrate": 151,
    "Zerg Cerebrate Daggoth": 152,
    "Unused Zerg Building2": 153,
    "Protoss Nexus": 154,
    "Protoss Robotics Facility": 155,
    "Protoss Pylon": 156,
    "Protoss Assimilator": 157,
    "Protoss Unused type   1": 158,
    "Unused Protoss Building1": 158,
    "Protoss Observatory": 159,
    "Protoss Gateway": 160,
    "Protoss Unused type   2": 161,
    "Unused Protoss Building2": 161,
    "Protoss Photon Cannon": 162,
    "Protoss Citadel of Adun": 163,
    "Protoss Cybernetics Core": 164,
    "Protoss Templar Archives": 165,
    "Protoss Forge": 166,
    "Protoss Stargate": 167,
    "Stasis Cell/Prison": 168,
    "Protoss Fleet Beacon": 169,
    "Protoss Arbiter Tribunal": 170,
    "Protoss Robotics Support Bay": 171,
    "Protoss Shield Battery": 172,
    "Khaydarin Crystal Formation": 173,
    "Protoss Temple": 174,
    "Xel'Naga Temple": 175,
    "Mineral Field (Type 1)": 176,
    "Mineral Field (Type 2)": 177,
    "Mineral Field (Type 3)": 178,
    "Cave": 179,
    "Cave (Unused)": 179,
    "Cave-in": 180,
    "Cave-in (Unused)": 180,
    "Cantina": 181,
    "Cantina (Unused)": 181,
    "Mining Platform": 182,
    "Mining Platform (Unused)": 182,
    "Independent Command Center": 183,
    "Independent Command Center (Unused)": 183,
    "Independent Starport": 184,
    "Independent Starport (Unused)": 184,
    "Jump Gate": 185,
    "Independent Jump Gate (Unused)": 185,
    "Ruins": 186,
    "Ruins (Unused)": 186,
    "Kyadarin Crystal Formation": 187,
    "Khaydarin Crystal Formation (Unused)": 187,
    "Vespene Geyser": 188,
    "Warp Gate": 189,
    "Psi Disrupter": 190,
    "Zerg Marker": 191,
    "Terran Marker": 192,
    "Protoss Marker": 193,
    "Zerg Beacon": 194,
    "Terran Beacon": 195,
    "Protoss Beacon": 196,
    "Zerg Flag Beacon": 197,
    "Terran Flag Beacon": 198,
    "Protoss Flag Beacon": 199,
    "Power Generator": 200,
    "Overmind Cocoon": 201,
    "Dark Swarm": 202,
    "Floor Missile Trap": 203,
    "Floor Hatch (Unused)": 204,
    "Floor Hatch (UNUSED)": 204,
    "Left Upper Level Door": 205,
    "Right Upper Level Door": 206,
    "Left Pit Door": 207,
    "Right Pit Door": 208,
    "Floor Gun Trap": 209,
    "Left Wall Missile Trap": 210,
    "Left Wall Flame Trap": 211,
    "Right Wall Missile Trap": 212,
    "Right Wall Flame Trap": 213,
    "Start Location": 214,
    "Flag": 215,
    "Young Chrysalis": 216,
    "Psi Emitter": 217,
    "Data Disc": 218,
    "Khaydarin Crystal": 219,
    "Mineral Chunk (Type 1)": 220,
    "Mineral Chunk (Type 2)": 221,
    "Mineral Cluster Type 1": 220,
    "Mineral Cluster Type 2": 221,
    "Vespene Orb (Protoss Type 1)": 222,
    "Vespene Orb (Protoss Type 2)": 223,
    "Protoss Vespene Gas Orb Type 1": 222,
    "Protoss Vespene Gas Orb Type 2": 223,
    "Vespene Sac (Zerg Type 1)": 224,
    "Vespene Sac (Zerg Type 2)": 225,
    "Zerg Vespene Gas Sac Type 1": 224,
    "Zerg Vespene Gas Sac Type 2": 225,
    "Vespene Tank (Terran Type 1)": 226,
    "Vespene Tank (Terran Type 2)": 227,
    "Terran Vespene Gas Tank Type 1": 226,
    "Terran Vespene Gas Tank Type 2": 227,
    "Unused unit 228": 228,
    "Unused228": 228,
    "None": 228,
    "Any unit": 229,
    "(any unit)": 229,
    "Men": 230,
    "(men)": 230,
    "Buildings": 231,
    "(buildings)": 231,
    "Factories": 232,
    "(factories)": 232,
}

DefaultUnit: TypeAlias = Literal[
    "Terran Marine",
    "Terran Ghost",
    "Terran Vulture",
    "Terran Goliath",
    "Goliath Turret",
    "Terran Siege Tank (Tank Mode)",
    "Siege Tank Turret (Tank Mode)",
    "Terran SCV",
    "Terran Wraith",
    "Terran Science Vessel",
    "Gui Montag",
    "Terran Dropship",
    "Terran Battlecruiser",
    "Vulture Spider Mine",
    "Nuclear Missile",
    "Terran Civilian",
    "Sarah Kerrigan",
    "Alan Schezar",
    "Alan Schezar Turret",
    "Jim Raynor (Vulture)",
    "Jim Raynor (Marine)",
    "Tom Kazansky",
    "Magellan",
    "Edmund Duke (Tank Mode)",
    "Edmund Duke Turret (Tank Mode)",
    "Edmund Duke (Siege Mode)",
    "Edmund Duke Turret (Siege Mode)",
    "Arcturus Mengsk",
    "Hyperion",
    "Norad II (Battlecruiser)",
    "Terran Siege Tank (Siege Mode)",
    "Siege Tank Turret (Siege Mode)",
    "Terran Firebat",
    "Scanner Sweep",
    "Terran Medic",
    "Zerg Larva",
    "Zerg Egg",
    "Zerg Zergling",
    "Zerg Hydralisk",
    "Zerg Ultralisk",
    "Zerg Broodling",
    "Zerg Drone",
    "Zerg Overlord",
    "Zerg Mutalisk",
    "Zerg Guardian",
    "Zerg Queen",
    "Zerg Defiler",
    "Zerg Scourge",
    "Torrasque",
    "Matriarch",
    "Infested Terran",
    "Infested Kerrigan",
    "Unclean One",
    "Hunter Killer",
    "Devouring One",
    "Kukulza (Mutalisk)",
    "Kukulza (Guardian)",
    "Yggdrasill",
    "Terran Valkyrie",
    "Cocoon",
    "Protoss Corsair",
    "Protoss Dark Templar",
    "Zerg Devourer",
    "Protoss Dark Archon",
    "Protoss Probe",
    "Protoss Zealot",
    "Protoss Dragoon",
    "Protoss High Templar",
    "Protoss Archon",
    "Protoss Shuttle",
    "Protoss Scout",
    "Protoss Arbiter",
    "Protoss Carrier",
    "Protoss Interceptor",
    "Dark Templar (Hero)",
    "Zeratul",
    "Tassadar/Zeratul",
    "Fenix (Zealot)",
    "Fenix (Dragoon)",
    "Tassadar",
    "Mojo"
    "Warbringer",
    "Gantrithor",
    "Protoss Reaver",
    "Protoss Observer",
    "Protoss Scarab",
    "Danimoth",
    "Aldaris",
    "Artanis",
    "Rhynadon",
    "Bengalaas",
    "Cargo Ship",
    "Mercenary Gunship",
    "Scantid",
    "Kakaru",
    "Ragnasaur",
    "Ursadon",
    "Lurker Egg",
    "Zerg Lurker Egg",
    "Raszagal",
    "Samir Duran",
    "Alexei Stukov",
    "Map Revealer",
    "Gerard DuGalle",
    "Zerg Lurker",
    "Infested Duran",
    "Disruption Web",
    "Terran Command Center",
    "Terran Comsat Station",
    "Terran Nuclear Silo",
    "Terran Supply Depot",
    "Terran Refinery",
    "Terran Barracks",
    "Terran Academy",
    "Terran Factory",
    "Terran Starport",
    "Terran Control Tower",
    "Terran Science Facility",
    "Terran Covert Ops",
    "Terran Physics Lab",
    "Starbase",
    "Terran Machine Shop",
    "Repair Bay",
    "Terran Engineering Bay",
    "Terran Armory",
    "Terran Missile Turret",
    "Terran Bunker",
    "Norad II (Crashed)",
    "Ion Cannon",
    "Uraj Crystal",
    "Khalis Crystal",
    "Infested Command Center",
    "Zerg Hatchery",
    "Zerg Lair",
    "Zerg Hive",
    "Zerg Nydus Canal",
    "Zerg Hydralisk Den",
    "Zerg Defiler Mound",
    "Zerg Greater Spire",
    "Zerg Queen's Nest",
    "Zerg Evolution Chamber",
    "Zerg Ultralisk Cavern",
    "Zerg Spire",
    "Zerg Spawning Pool",
    "Zerg Creep Colony",
    "Zerg Spore Colony",
    "Unused Zerg Building1",
    "Zerg Sunken Colony",
    "Zerg Overmind (With Shell)",
    "Zerg Overmind",
    "Zerg Extractor",
    "Mature Chrysalis",
    "Zerg Cerebrate",
    "Zerg Cerebrate Daggoth",
    "Unused Zerg Building2",
    "Protoss Nexus",
    "Protoss Robotics Facility",
    "Protoss Pylon",
    "Protoss Assimilator",
    "Unused Protoss Building1",
    "Protoss Observatory",
    "Protoss Gateway",
    "Unused Protoss Building2",
    "Protoss Photon Cannon",
    "Protoss Citadel of Adun",
    "Protoss Cybernetics Core",
    "Protoss Templar Archives",
    "Protoss Forge",
    "Protoss Stargate",
    "Stasis Cell/Prison",
    "Protoss Fleet Beacon",
    "Protoss Arbiter Tribunal",
    "Protoss Robotics Support Bay",
    "Protoss Shield Battery",
    "Khaydarin Crystal Formation",
    "Protoss Temple",
    "Xel'Naga Temple",
    "Mineral Field (Type 1)",
    "Mineral Field (Type 2)",
    "Mineral Field (Type 3)",
    "Cave",
    "Cave-in",
    "Cantina",
    "Mining Platform",
    "Independent Command Center",
    "Independent Starport",
    "Jump Gate",
    "Ruins",
    "Khaydarin Crystal Formation (Unused)",
    "Vespene Geyser",
    "Warp Gate",
    "Psi Disrupter",
    "Zerg Marker",
    "Terran Marker",
    "Protoss Marker",
    "Zerg Beacon",
    "Terran Beacon",
    "Protoss Beacon",
    "Zerg Flag Beacon",
    "Terran Flag Beacon",
    "Protoss Flag Beacon",
    "Power Generator",
    "Overmind Cocoon",
    "Dark Swarm",
    "Floor Missile Trap",
    "Floor Hatch (Unused)",
    "Left Upper Level Door",
    "Right Upper Level Door",
    "Left Pit Door",
    "Right Pit Door",
    "Floor Gun Trap",
    "Left Wall Missile Trap",
    "Left Wall Flame Trap",
    "Right Wall Missile Trap",
    "Right Wall Flame Trap",
    "Start Location",
    "Flag",
    "Young Chrysalis",
    "Psi Emitter",
    "Data Disc",
    "Khaydarin Crystal",
    "Mineral Chunk (Type 1)",
    "Mineral Chunk (Type 2)",
    "Vespene Orb (Protoss Type 1)",
    "Vespene Orb (Protoss Type 2)",
    "Vespene Sac (Zerg Type 1)",
    "Vespene Sac (Zerg Type 2)",
    "Vespene Tank (Terran Type 1)",
    "Vespene Tank (Terran Type 2)",
    "None",
    "(any unit)",
    "(men)",
    "(buildings)",
    "(factories)",
]

# ======================================

# Data from http://cafe.daum.net/rpgguild/6cWR/158
# Original data from ScAIEdit
DefAIScriptDict: dict[bytes, bytes] = {
    # Custom AI Scripts
    b"Terran Custom Level": b"TMCu",
    b"Zerg Custom Level": b"ZMCu",
    b"Protoss Custom Level": b"PMCu",
    b"Terran Expansion Custom Level": b"TMCx",
    b"Zerg Expansion Custom Level": b"ZMCx",
    b"Protoss Expansion Custom Level": b"PMCx",
    b"Terran Campaign Easy": b"TLOf",
    b"Terran Campaign Medium": b"TMED",
    b"Terran Campaign Difficult": b"THIf",
    b"Terran Campaign Insane": b"TSUP",
    b"Terran Campaign Area Town": b"TARE",
    b"Zerg Campaign Easy": b"ZLOf",
    b"Zerg Campaign Medium": b"ZMED",
    b"Zerg Campaign Difficult": b"ZHIf",
    b"Zerg Campaign Insane": b"ZSUP",
    b"Zerg Campaign Area Town": b"ZARE",
    b"Protoss Campaign Easy": b"PLOf",
    b"Protoss Campaign Medium": b"PMED",
    b"Protoss Campaign Difficult": b"PHIf",
    b"Protoss Campaign Insane": b"PSUP",
    b"Protoss Campaign Area Town": b"PARE",
    b"Expansion Terran Campaign Easy": b"TLOx",
    b"Expansion Terran Campaign Medium": b"TMEx",
    b"Expansion Terran Campaign Difficult": b"THIx",
    b"Expansion Terran Campaign Insane": b"TSUx",
    b"Expansion Terran Campaign Area Town": b"TARx",
    b"Expansion Zerg Campaign Easy": b"ZLOx",
    b"Expansion Zerg Campaign Medium": b"ZMEx",
    b"Expansion Zerg Campaign Difficult": b"ZHIx",
    b"Expansion Zerg Campaign Insane": b"ZSUx",
    b"Expansion Zerg Campaign Area Town": b"ZARx",
    b"Expansion Protoss Campaign Easy": b"PLOx",
    b"Expansion Protoss Campaign Medium": b"PMEx",
    b"Expansion Protoss Campaign Difficult": b"PHIx",
    b"Expansion Protoss Campaign Insane": b"PSUx",
    b"Expansion Protoss Campaign Area Town": b"PARx",
    b"Send All Units on Strategic Suicide Missions": b"Suic",
    b"Send All Units on Random Suicide Missions": b"SuiR",
    b"Switch Computer Player to Rescue Passive": b"Rscu",
    b"Turn ON Shared Vision for Player 1": b"+Vi0",
    b"Turn ON Shared Vision for Player 2": b"+Vi1",
    b"Turn ON Shared Vision for Player 3": b"+Vi2",
    b"Turn ON Shared Vision for Player 4": b"+Vi3",
    b"Turn ON Shared Vision for Player 5": b"+Vi4",
    b"Turn ON Shared Vision for Player 6": b"+Vi5",
    b"Turn ON Shared Vision for Player 7": b"+Vi6",
    b"Turn ON Shared Vision for Player 8": b"+Vi7",
    b"Turn OFF Shared Vision for Player 1": b"-Vi0",
    b"Turn OFF Shared Vision for Player 2": b"-Vi1",
    b"Turn OFF Shared Vision for Player 3": b"-Vi2",
    b"Turn OFF Shared Vision for Player 4": b"-Vi3",
    b"Turn OFF Shared Vision for Player 5": b"-Vi4",
    b"Turn OFF Shared Vision for Player 6": b"-Vi5",
    b"Turn OFF Shared Vision for Player 7": b"-Vi6",
    b"Turn OFF Shared Vision for Player 8": b"-Vi7",
    b"Move Dark Templars to Region": b"MvTe",
    b"Clear Previous Combat Data": b"ClrC",
    b"Set Player to Enemy": b"Enmy",
    b"Set Player to Ally": b"Ally",
    b"Value This Area Higher": b"VluA",
    b"Enter Closest Bunker": b"EnBk",
    b"Set Generic Command Target": b"StTg",
    b"Make These Units Patrol": b"StPt",
    b"Enter Transport": b"EnTr",
    b"Exit Transport": b"ExTr",
    b"AI Nuke Here": b"NuHe",
    b"AI Harass Here": b"HaHe",
    b"Set Unit Order To: Junk Yard Dog": b"JYDg",
    b"Disruption Web Here": b"DWHe",
    b"Recall Here": b"ReHe",
    # StarCraft AI Scripts
    b"Terran 3 - Zerg Town": b"Ter3",
    b"Terran 5 - Terran Main Town": b"Ter5",
    b"Terran 5 - Terran Harvest Town": b"Te5H",
    b"Terran 6 - Air Attack Zerg": b"Ter6",
    b"Terran 6 - Ground Attack Zerg": b"Te6b",
    b"Terran 6 - Zerg Support Town": b"Te6c",
    b"Terran 7 - Bottom Zerg Town": b"Ter7",
    b"Terran 7 - Right Zerg Town": b"Te7s",
    b"Terran 7 - Middle Zerg Town": b"Te7m",
    b"Terran 8 - Confederate Town": b"Ter8",
    b"Terran 9 - Light Attack": b"Tr9L",
    b"Terran 9 - Heavy Attack": b"Tr9H",
    b"Terran 10 - Confederate Towns": b"Te10",
    b"Terran 11 - Zerg Town": b"T11z",
    b"Terran 11 - Lower Protoss Town": b"T11a",
    b"Terran 11 - Upper Protoss Town": b"T11b",
    b"Terran 12 - Nuke Town": b"T12N",
    b"Terran 12 - Phoenix Town": b"T12P",
    b"Terran 12 - Tank Town": b"T12T",
    b"Terran 1 - Electronic Distribution": b"TED1",
    b"Terran 2 - Electronic Distribution": b"TED2",
    b"Terran 3 - Electronic Distribution": b"TED3",
    b"Terran 1 - Shareware": b"TSW1",
    b"Terran 2 - Shareware": b"TSW2",
    b"Terran 3 - Shareware": b"TSW3",
    b"Terran 4 - Shareware": b"TSW4",
    b"Terran 5 - Shareware": b"TSW5",
    b"Zerg 1 - Terran Town": b"Zer1",
    b"Zerg 2 - Protoss Town": b"Zer2",
    b"Zerg 3 - Terran Town": b"Zer3",
    b"Zerg 4 - Right Terran Town": b"Zer4",
    b"Zerg 4 - Lower Terran Town": b"Ze4S",
    b"Zerg 6 - Protoss Town": b"Zer6",
    b"Zerg 7 - Air Town": b"Zr7a",
    b"Zerg 7 - Ground Town": b"Zr7g",
    b"Zerg 7 - Support Town": b"Zr7s",
    b"Zerg 8 - Scout Town": b"Zer8",
    b"Zerg 8 - Templar Town": b"Ze8T",
    b"Zerg 9 - Teal Protoss": b"Zer9",
    b"Zerg 9 - Left Yellow Protoss": b"Z9ly",
    b"Zerg 9 - Right Yellow Protoss": b"Z9ry",
    b"Zerg 9 - Left Orange Protoss": b"Z9lo",
    b"Zerg 9 - Right Orange Protoss": b"Z9ro",
    b"Zerg 10 - Left Teal (Attack": b"Z10a",
    b"Zerg 10 - Right Teal (Support": b"Z10b",
    b"Zerg 10 - Left Yellow (Support": b"Z10c",
    b"Zerg 10 - Right Yellow (Attack": b"Z10d",
    b"Zerg 10 - Red Protoss": b"Z10e",
    b"Protoss 1 - Zerg Town": b"Pro1",
    b"Protoss 2 - Zerg Town": b"Pro2",
    b"Protoss 3 - Air Zerg Town": b"Pr3R",
    b"Protoss 3 - Ground Zerg Town": b"Pr3G",
    b"Protoss 4 - Zerg Town": b"Pro4",
    b"Protoss 5 - Zerg Town Island": b"Pr5I",
    b"Protoss 5 - Zerg Town Base": b"Pr5B",
    b"Protoss 7 - Left Protoss Town": b"Pro7",
    b"Protoss 7 - Right Protoss Town": b"Pr7B",
    b"Protoss 7 - Shrine Protoss": b"Pr7S",
    b"Protoss 8 - Left Protoss Town": b"Pro8",
    b"Protoss 8 - Right Protoss Town": b"Pr8B",
    b"Protoss 8 - Protoss Defenders": b"Pr8D",
    b"Protoss 9 - Ground Zerg": b"Pro9",
    b"Protoss 9 - Air Zerg": b"Pr9W",
    b"Protoss 9 - Spell Zerg": b"Pr9Y",
    b"Protoss 10 - Mini-Towns": b"Pr10",
    b"Protoss 10 - Mini-Town Master": b"P10C",
    b"Protoss 10 - Overmind Defenders": b"P10o",
    # Brood Wars AI Scripts
    b"Brood Wars Protoss 1 - Town A": b"PB1A",
    b"Brood Wars Protoss 1 - Town B": b"PB1B",
    b"Brood Wars Protoss 1 - Town C": b"PB1C",
    b"Brood Wars Protoss 1 - Town D": b"PB1D",
    b"Brood Wars Protoss 1 - Town E": b"PB1E",
    b"Brood Wars Protoss 1 - Town F": b"PB1F",
    b"Brood Wars Protoss 2 - Town A": b"PB2A",
    b"Brood Wars Protoss 2 - Town B": b"PB2B",
    b"Brood Wars Protoss 2 - Town C": b"PB2C",
    b"Brood Wars Protoss 2 - Town D": b"PB2D",
    b"Brood Wars Protoss 2 - Town E": b"PB2E",
    b"Brood Wars Protoss 2 - Town F": b"PB2F",
    b"Brood Wars Protoss 3 - Town A": b"PB3A",
    b"Brood Wars Protoss 3 - Town B": b"PB3B",
    b"Brood Wars Protoss 3 - Town C": b"PB3C",
    b"Brood Wars Protoss 3 - Town D": b"PB3D",
    b"Brood Wars Protoss 3 - Town E": b"PB3E",
    b"Brood Wars Protoss 3 - Town F": b"PB3F",
    b"Brood Wars Protoss 4 - Town A": b"PB4A",
    b"Brood Wars Protoss 4 - Town B": b"PB4B",
    b"Brood Wars Protoss 4 - Town C": b"PB4C",
    b"Brood Wars Protoss 4 - Town D": b"PB4D",
    b"Brood Wars Protoss 4 - Town E": b"PB4E",
    b"Brood Wars Protoss 4 - Town F": b"PB4F",
    b"Brood Wars Protoss 5 - Town A": b"PB5A",
    b"Brood Wars Protoss 5 - Town B": b"PB5B",
    b"Brood Wars Protoss 5 - Town C": b"PB5C",
    b"Brood Wars Protoss 5 - Town D": b"PB5D",
    b"Brood Wars Protoss 5 - Town E": b"PB5E",
    b"Brood Wars Protoss 5 - Town F": b"PB5F",
    b"Brood Wars Protoss 6 - Town A": b"PB6A",
    b"Brood Wars Protoss 6 - Town B": b"PB6B",
    b"Brood Wars Protoss 6 - Town C": b"PB6C",
    b"Brood Wars Protoss 6 - Town D": b"PB6D",
    b"Brood Wars Protoss 6 - Town E": b"PB6E",
    b"Brood Wars Protoss 6 - Town F": b"PB6F",
    b"Brood Wars Protoss 7 - Town A": b"PB7A",
    b"Brood Wars Protoss 7 - Town B": b"PB7B",
    b"Brood Wars Protoss 7 - Town C": b"PB7C",
    b"Brood Wars Protoss 7 - Town D": b"PB7D",
    b"Brood Wars Protoss 7 - Town E": b"PB7E",
    b"Brood Wars Protoss 7 - Town F": b"PB7F",
    b"Brood Wars Protoss 8 - Town A": b"PB8A",
    b"Brood Wars Protoss 8 - Town B": b"PB8B",
    b"Brood Wars Protoss 8 - Town C": b"PB8C",
    b"Brood Wars Protoss 8 - Town D": b"PB8D",
    b"Brood Wars Protoss 8 - Town E": b"PB8E",
    b"Brood Wars Protoss 8 - Town F": b"PB8F",
    b"Brood Wars Terran 1 - Town A": b"TB1A",
    b"Brood Wars Terran 1 - Town B": b"TB1B",
    b"Brood Wars Terran 1 - Town C": b"TB1C",
    b"Brood Wars Terran 1 - Town D": b"TB1D",
    b"Brood Wars Terran 1 - Town E": b"TB1E",
    b"Brood Wars Terran 1 - Town F": b"TB1F",
    b"Brood Wars Terran 2 - Town A": b"TB2A",
    b"Brood Wars Terran 2 - Town B": b"TB2B",
    b"Brood Wars Terran 2 - Town C": b"TB2C",
    b"Brood Wars Terran 2 - Town D": b"TB2D",
    b"Brood Wars Terran 2 - Town E": b"TB2E",
    b"Brood Wars Terran 2 - Town F": b"TB2F",
    b"Brood Wars Terran 3 - Town A": b"TB3A",
    b"Brood Wars Terran 3 - Town B": b"TB3B",
    b"Brood Wars Terran 3 - Town C": b"TB3C",
    b"Brood Wars Terran 3 - Town D": b"TB3D",
    b"Brood Wars Terran 3 - Town E": b"TB3E",
    b"Brood Wars Terran 3 - Town F": b"TB3F",
    b"Brood Wars Terran 4 - Town A": b"TB4A",
    b"Brood Wars Terran 4 - Town B": b"TB4B",
    b"Brood Wars Terran 4 - Town C": b"TB4C",
    b"Brood Wars Terran 4 - Town D": b"TB4D",
    b"Brood Wars Terran 4 - Town E": b"TB4E",
    b"Brood Wars Terran 4 - Town F": b"TB4F",
    b"Brood Wars Terran 5 - Town A": b"TB5A",
    b"Brood Wars Terran 5 - Town B": b"TB5B",
    b"Brood Wars Terran 5 - Town C": b"TB5C",
    b"Brood Wars Terran 5 - Town D": b"TB5D",
    b"Brood Wars Terran 5 - Town E": b"TB5E",
    b"Brood Wars Terran 5 - Town F": b"TB5F",
    b"Brood Wars Terran 6 - Town A": b"TB6A",
    b"Brood Wars Terran 6 - Town B": b"TB6B",
    b"Brood Wars Terran 6 - Town C": b"TB6C",
    b"Brood Wars Terran 6 - Town D": b"TB6D",
    b"Brood Wars Terran 6 - Town E": b"TB6E",
    b"Brood Wars Terran 6 - Town F": b"TB6F",
    b"Brood Wars Terran 7 - Town A": b"TB7A",
    b"Brood Wars Terran 7 - Town B": b"TB7B",
    b"Brood Wars Terran 7 - Town C": b"TB7C",
    b"Brood Wars Terran 7 - Town D": b"TB7D",
    b"Brood Wars Terran 7 - Town E": b"TB7E",
    b"Brood Wars Terran 7 - Town F": b"TB7F",
    b"Brood Wars Terran 8 - Town A": b"TB8A",
    b"Brood Wars Terran 8 - Town B": b"TB8B",
    b"Brood Wars Terran 8 - Town C": b"TB8C",
    b"Brood Wars Terran 8 - Town D": b"TB8D",
    b"Brood Wars Terran 8 - Town E": b"TB8E",
    b"Brood Wars Terran 8 - Town F": b"TB8F",
    b"Brood Wars Zerg 1 - Town A": b"ZB1A",
    b"Brood Wars Zerg 1 - Town B": b"ZB1B",
    b"Brood Wars Zerg 1 - Town C": b"ZB1C",
    b"Brood Wars Zerg 1 - Town D": b"ZB1D",
    b"Brood Wars Zerg 1 - Town E": b"ZB1E",
    b"Brood Wars Zerg 1 - Town F": b"ZB1F",
    b"Brood Wars Zerg 2 - Town A": b"ZB2A",
    b"Brood Wars Zerg 2 - Town B": b"ZB2B",
    b"Brood Wars Zerg 2 - Town C": b"ZB2C",
    b"Brood Wars Zerg 2 - Town D": b"ZB2D",
    b"Brood Wars Zerg 2 - Town E": b"ZB2E",
    b"Brood Wars Zerg 2 - Town F": b"ZB2F",
    b"Brood Wars Zerg 3 - Town A": b"ZB3A",
    b"Brood Wars Zerg 3 - Town B": b"ZB3B",
    b"Brood Wars Zerg 3 - Town C": b"ZB3C",
    b"Brood Wars Zerg 3 - Town D": b"ZB3D",
    b"Brood Wars Zerg 3 - Town E": b"ZB3E",
    b"Brood Wars Zerg 3 - Town F": b"ZB3F",
    b"Brood Wars Zerg 4 - Town A": b"ZB4A",
    b"Brood Wars Zerg 4 - Town B": b"ZB4B",
    b"Brood Wars Zerg 4 - Town C": b"ZB4C",
    b"Brood Wars Zerg 4 - Town D": b"ZB4D",
    b"Brood Wars Zerg 4 - Town E": b"ZB4E",
    b"Brood Wars Zerg 4 - Town F": b"ZB4F",
    b"Brood Wars Zerg 5 - Town A": b"ZB5A",
    b"Brood Wars Zerg 5 - Town B": b"ZB5B",
    b"Brood Wars Zerg 5 - Town C": b"ZB5C",
    b"Brood Wars Zerg 5 - Town D": b"ZB5D",
    b"Brood Wars Zerg 5 - Town E": b"ZB5E",
    b"Brood Wars Zerg 5 - Town F": b"ZB5F",
    b"Brood Wars Zerg 6 - Town A": b"ZB6A",
    b"Brood Wars Zerg 6 - Town B": b"ZB6B",
    b"Brood Wars Zerg 6 - Town C": b"ZB6C",
    b"Brood Wars Zerg 6 - Town D": b"ZB6D",
    b"Brood Wars Zerg 6 - Town E": b"ZB6E",
    b"Brood Wars Zerg 6 - Town F": b"ZB6F",
    b"Brood Wars Zerg 7 - Town A": b"ZB7A",
    b"Brood Wars Zerg 7 - Town B": b"ZB7B",
    b"Brood Wars Zerg 7 - Town C": b"ZB7C",
    b"Brood Wars Zerg 7 - Town D": b"ZB7D",
    b"Brood Wars Zerg 7 - Town E": b"ZB7E",
    b"Brood Wars Zerg 7 - Town F": b"ZB7F",
    b"Brood Wars Zerg 8 - Town A": b"ZB8A",
    b"Brood Wars Zerg 8 - Town B": b"ZB8B",
    b"Brood Wars Zerg 8 - Town C": b"ZB8C",
    b"Brood Wars Zerg 8 - Town D": b"ZB8D",
    b"Brood Wars Zerg 8 - Town E": b"ZB8E",
    b"Brood Wars Zerg 8 - Town F": b"ZB8F",
    b"Brood Wars Zerg 9 - Town A": b"ZB9A",
    b"Brood Wars Zerg 9 - Town B": b"ZB9B",
    b"Brood Wars Zerg 9 - Town C": b"ZB9C",
    b"Brood Wars Zerg 9 - Town D": b"ZB9D",
    b"Brood Wars Zerg 9 - Town E": b"ZB9E",
    b"Brood Wars Zerg 9 - Town F": b"ZB9F",
    b"Brood Wars Zerg 10 - Town A": b"ZB0A",
    b"Brood Wars Zerg 10 - Town B": b"ZB0B",
    b"Brood Wars Zerg 10 - Town C": b"ZB0C",
    b"Brood Wars Zerg 10 - Town D": b"ZB0D",
    b"Brood Wars Zerg 10 - Town E": b"ZB0E",
    b"Brood Wars Zerg 10 - Town F": b"ZB0F",
}

DefaultAIScriptWithoutLocation: TypeAlias = Literal[
    "Send All Units on Strategic Suicide Missions",
    "Send All Units on Random Suicide Missions",
    "Switch Computer Player to Rescue Passive",
    "Turn ON Shared Vision for Player 1",
    "Turn ON Shared Vision for Player 2",
    "Turn ON Shared Vision for Player 3",
    "Turn ON Shared Vision for Player 4",
    "Turn ON Shared Vision for Player 5",
    "Turn ON Shared Vision for Player 6",
    "Turn ON Shared Vision for Player 7",
    "Turn ON Shared Vision for Player 8",
    "Turn OFF Shared Vision for Player 1",
    "Turn OFF Shared Vision for Player 2",
    "Turn OFF Shared Vision for Player 3",
    "Turn OFF Shared Vision for Player 4",
    "Turn OFF Shared Vision for Player 5",
    "Turn OFF Shared Vision for Player 6",
    "Turn OFF Shared Vision for Player 7",
    "Turn OFF Shared Vision for Player 8",
]

DefaultAIScriptAtLocation: TypeAlias = Literal[
    "Terran Custom Level",
    "Zerg Custom Level",
    "Protoss Custom Level",
    "Terran Expansion Custom Level",
    "Zerg Expansion Custom Level",
    "Protoss Expansion Custom Level",
    "Terran Campaign Easy",
    "Terran Campaign Medium",
    "Terran Campaign Difficult",
    "Terran Campaign Insane",
    "Terran Campaign Area Town",
    "Zerg Campaign Easy",
    "Zerg Campaign Medium",
    "Zerg Campaign Difficult",
    "Zerg Campaign Insane",
    "Zerg Campaign Area Town",
    "Protoss Campaign Easy",
    "Protoss Campaign Medium",
    "Protoss Campaign Difficult",
    "Protoss Campaign Insane",
    "Protoss Campaign Area Town",
    "Expansion Terran Campaign Easy",
    "Expansion Terran Campaign Medium",
    "Expansion Terran Campaign Difficult",
    "Expansion Terran Campaign Insane",
    "Expansion Terran Campaign Area Town",
    "Expansion Zerg Campaign Easy",
    "Expansion Zerg Campaign Medium",
    "Expansion Zerg Campaign Difficult",
    "Expansion Zerg Campaign Insane",
    "Expansion Zerg Campaign Area Town",
    "Expansion Protoss Campaign Easy",
    "Expansion Protoss Campaign Medium",
    "Expansion Protoss Campaign Difficult",
    "Expansion Protoss Campaign Insane",
    "Expansion Protoss Campaign Area Town",
    "Move Dark Templars to Region",
    "Clear Previous Combat Data",
    "Set Player to Enemy",
    "Set Player to Ally",
    "Value This Area Higher",
    "Enter Closest Bunker",
    "Set Generic Command Target",
    "Make These Units Patrol",
    "Enter Transport",
    "Exit Transport",
    "AI Nuke Here",
    "AI Harass Here",
    "Set Unit Order To: Junk Yard Dog",
    "Disruption Web Here",
    "Recall Here",
    "Terran 3 - Zerg Town",
    "Terran 5 - Terran Main Town",
    "Terran 5 - Terran Harvest Town",
    "Terran 6 - Air Attack Zerg",
    "Terran 6 - Ground Attack Zerg",
    "Terran 6 - Zerg Support Town",
    "Terran 7 - Bottom Zerg Town",
    "Terran 7 - Right Zerg Town",
    "Terran 7 - Middle Zerg Town",
    "Terran 8 - Confederate Town",
    "Terran 9 - Light Attack",
    "Terran 9 - Heavy Attack",
    "Terran 10 - Confederate Towns",
    "Terran 11 - Zerg Town",
    "Terran 11 - Lower Protoss Town",
    "Terran 11 - Upper Protoss Town",
    "Terran 12 - Nuke Town",
    "Terran 12 - Phoenix Town",
    "Terran 12 - Tank Town",
    "Terran 1 - Electronic Distribution",
    "Terran 2 - Electronic Distribution",
    "Terran 3 - Electronic Distribution",
    "Terran 1 - Shareware",
    "Terran 2 - Shareware",
    "Terran 3 - Shareware",
    "Terran 4 - Shareware",
    "Terran 5 - Shareware",
    "Zerg 1 - Terran Town",
    "Zerg 2 - Protoss Town",
    "Zerg 3 - Terran Town",
    "Zerg 4 - Right Terran Town",
    "Zerg 4 - Lower Terran Town",
    "Zerg 6 - Protoss Town",
    "Zerg 7 - Air Town",
    "Zerg 7 - Ground Town",
    "Zerg 7 - Support Town",
    "Zerg 8 - Scout Town",
    "Zerg 8 - Templar Town",
    "Zerg 9 - Teal Protoss",
    "Zerg 9 - Left Yellow Protoss",
    "Zerg 9 - Right Yellow Protoss",
    "Zerg 9 - Left Orange Protoss",
    "Zerg 9 - Right Orange Protoss",
    "Zerg 10 - Left Teal (Attack",
    "Zerg 10 - Right Teal (Support",
    "Zerg 10 - Left Yellow (Support",
    "Zerg 10 - Right Yellow (Attack",
    "Zerg 10 - Red Protoss",
    "Protoss 1 - Zerg Town",
    "Protoss 2 - Zerg Town",
    "Protoss 3 - Air Zerg Town",
    "Protoss 3 - Ground Zerg Town",
    "Protoss 4 - Zerg Town",
    "Protoss 5 - Zerg Town Island",
    "Protoss 5 - Zerg Town Base",
    "Protoss 7 - Left Protoss Town",
    "Protoss 7 - Right Protoss Town",
    "Protoss 7 - Shrine Protoss",
    "Protoss 8 - Left Protoss Town",
    "Protoss 8 - Right Protoss Town",
    "Protoss 8 - Protoss Defenders",
    "Protoss 9 - Ground Zerg",
    "Protoss 9 - Air Zerg",
    "Protoss 9 - Spell Zerg",
    "Protoss 10 - Mini-Towns",
    "Protoss 10 - Mini-Town Master",
    "Protoss 10 - Overmind Defenders",
    "Brood Wars Protoss 1 - Town A",
    "Brood Wars Protoss 1 - Town B",
    "Brood Wars Protoss 1 - Town C",
    "Brood Wars Protoss 1 - Town D",
    "Brood Wars Protoss 1 - Town E",
    "Brood Wars Protoss 1 - Town F",
    "Brood Wars Protoss 2 - Town A",
    "Brood Wars Protoss 2 - Town B",
    "Brood Wars Protoss 2 - Town C",
    "Brood Wars Protoss 2 - Town D",
    "Brood Wars Protoss 2 - Town E",
    "Brood Wars Protoss 2 - Town F",
    "Brood Wars Protoss 3 - Town A",
    "Brood Wars Protoss 3 - Town B",
    "Brood Wars Protoss 3 - Town C",
    "Brood Wars Protoss 3 - Town D",
    "Brood Wars Protoss 3 - Town E",
    "Brood Wars Protoss 3 - Town F",
    "Brood Wars Protoss 4 - Town A",
    "Brood Wars Protoss 4 - Town B",
    "Brood Wars Protoss 4 - Town C",
    "Brood Wars Protoss 4 - Town D",
    "Brood Wars Protoss 4 - Town E",
    "Brood Wars Protoss 4 - Town F",
    "Brood Wars Protoss 5 - Town A",
    "Brood Wars Protoss 5 - Town B",
    "Brood Wars Protoss 5 - Town C",
    "Brood Wars Protoss 5 - Town D",
    "Brood Wars Protoss 5 - Town E",
    "Brood Wars Protoss 5 - Town F",
    "Brood Wars Protoss 6 - Town A",
    "Brood Wars Protoss 6 - Town B",
    "Brood Wars Protoss 6 - Town C",
    "Brood Wars Protoss 6 - Town D",
    "Brood Wars Protoss 6 - Town E",
    "Brood Wars Protoss 6 - Town F",
    "Brood Wars Protoss 7 - Town A",
    "Brood Wars Protoss 7 - Town B",
    "Brood Wars Protoss 7 - Town C",
    "Brood Wars Protoss 7 - Town D",
    "Brood Wars Protoss 7 - Town E",
    "Brood Wars Protoss 7 - Town F",
    "Brood Wars Protoss 8 - Town A",
    "Brood Wars Protoss 8 - Town B",
    "Brood Wars Protoss 8 - Town C",
    "Brood Wars Protoss 8 - Town D",
    "Brood Wars Protoss 8 - Town E",
    "Brood Wars Protoss 8 - Town F",
    "Brood Wars Terran 1 - Town A",
    "Brood Wars Terran 1 - Town B",
    "Brood Wars Terran 1 - Town C",
    "Brood Wars Terran 1 - Town D",
    "Brood Wars Terran 1 - Town E",
    "Brood Wars Terran 1 - Town F",
    "Brood Wars Terran 2 - Town A",
    "Brood Wars Terran 2 - Town B",
    "Brood Wars Terran 2 - Town C",
    "Brood Wars Terran 2 - Town D",
    "Brood Wars Terran 2 - Town E",
    "Brood Wars Terran 2 - Town F",
    "Brood Wars Terran 3 - Town A",
    "Brood Wars Terran 3 - Town B",
    "Brood Wars Terran 3 - Town C",
    "Brood Wars Terran 3 - Town D",
    "Brood Wars Terran 3 - Town E",
    "Brood Wars Terran 3 - Town F",
    "Brood Wars Terran 4 - Town A",
    "Brood Wars Terran 4 - Town B",
    "Brood Wars Terran 4 - Town C",
    "Brood Wars Terran 4 - Town D",
    "Brood Wars Terran 4 - Town E",
    "Brood Wars Terran 4 - Town F",
    "Brood Wars Terran 5 - Town A",
    "Brood Wars Terran 5 - Town B",
    "Brood Wars Terran 5 - Town C",
    "Brood Wars Terran 5 - Town D",
    "Brood Wars Terran 5 - Town E",
    "Brood Wars Terran 5 - Town F",
    "Brood Wars Terran 6 - Town A",
    "Brood Wars Terran 6 - Town B",
    "Brood Wars Terran 6 - Town C",
    "Brood Wars Terran 6 - Town D",
    "Brood Wars Terran 6 - Town E",
    "Brood Wars Terran 6 - Town F",
    "Brood Wars Terran 7 - Town A",
    "Brood Wars Terran 7 - Town B",
    "Brood Wars Terran 7 - Town C",
    "Brood Wars Terran 7 - Town D",
    "Brood Wars Terran 7 - Town E",
    "Brood Wars Terran 7 - Town F",
    "Brood Wars Terran 8 - Town A",
    "Brood Wars Terran 8 - Town B",
    "Brood Wars Terran 8 - Town C",
    "Brood Wars Terran 8 - Town D",
    "Brood Wars Terran 8 - Town E",
    "Brood Wars Terran 8 - Town F",
    "Brood Wars Zerg 1 - Town A",
    "Brood Wars Zerg 1 - Town B",
    "Brood Wars Zerg 1 - Town C",
    "Brood Wars Zerg 1 - Town D",
    "Brood Wars Zerg 1 - Town E",
    "Brood Wars Zerg 1 - Town F",
    "Brood Wars Zerg 2 - Town A",
    "Brood Wars Zerg 2 - Town B",
    "Brood Wars Zerg 2 - Town C",
    "Brood Wars Zerg 2 - Town D",
    "Brood Wars Zerg 2 - Town E",
    "Brood Wars Zerg 2 - Town F",
    "Brood Wars Zerg 3 - Town A",
    "Brood Wars Zerg 3 - Town B",
    "Brood Wars Zerg 3 - Town C",
    "Brood Wars Zerg 3 - Town D",
    "Brood Wars Zerg 3 - Town E",
    "Brood Wars Zerg 3 - Town F",
    "Brood Wars Zerg 4 - Town A",
    "Brood Wars Zerg 4 - Town B",
    "Brood Wars Zerg 4 - Town C",
    "Brood Wars Zerg 4 - Town D",
    "Brood Wars Zerg 4 - Town E",
    "Brood Wars Zerg 4 - Town F",
    "Brood Wars Zerg 5 - Town A",
    "Brood Wars Zerg 5 - Town B",
    "Brood Wars Zerg 5 - Town C",
    "Brood Wars Zerg 5 - Town D",
    "Brood Wars Zerg 5 - Town E",
    "Brood Wars Zerg 5 - Town F",
    "Brood Wars Zerg 6 - Town A",
    "Brood Wars Zerg 6 - Town B",
    "Brood Wars Zerg 6 - Town C",
    "Brood Wars Zerg 6 - Town D",
    "Brood Wars Zerg 6 - Town E",
    "Brood Wars Zerg 6 - Town F",
    "Brood Wars Zerg 7 - Town A",
    "Brood Wars Zerg 7 - Town B",
    "Brood Wars Zerg 7 - Town C",
    "Brood Wars Zerg 7 - Town D",
    "Brood Wars Zerg 7 - Town E",
    "Brood Wars Zerg 7 - Town F",
    "Brood Wars Zerg 8 - Town A",
    "Brood Wars Zerg 8 - Town B",
    "Brood Wars Zerg 8 - Town C",
    "Brood Wars Zerg 8 - Town D",
    "Brood Wars Zerg 8 - Town E",
    "Brood Wars Zerg 8 - Town F",
    "Brood Wars Zerg 9 - Town A",
    "Brood Wars Zerg 9 - Town B",
    "Brood Wars Zerg 9 - Town C",
    "Brood Wars Zerg 9 - Town D",
    "Brood Wars Zerg 9 - Town E",
    "Brood Wars Zerg 9 - Town F",
    "Brood Wars Zerg 10 - Town A",
    "Brood Wars Zerg 10 - Town B",
    "Brood Wars Zerg 10 - Town C",
    "Brood Wars Zerg 10 - Town D",
    "Brood Wars Zerg 10 - Town E",
    "Brood Wars Zerg 10 - Town F",
]