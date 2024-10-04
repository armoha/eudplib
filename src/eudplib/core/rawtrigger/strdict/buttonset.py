from typing import Literal, TypeAlias

DefButtonSetDict: dict[str, int] = {
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
    "None": 228,
    "Cancel Order": 229,
    "Cancel Place COP": 230,
    "Building Is Constructed (Terran&Protoss)": 231,
    "Rallyable Building Is Constructed (Terran&Protoss)": 232,
    "Building Is Mutating (Zerg)": 233,
    "Rallyable Building Is Mutating (Zerg)": 234,
    "Cancel Infestation": 235,
    "Cancel Mutation (Lair&Hive)": 236,
    "Cancel Nuclear Strike": 237,
    "Zerg Basic Mutation": 238,
    "Terran Basic Structure": 239,
    "Protoss Basic Structure": 240,
    "Zerg Advanced Mutation": 241,
    "Terran Advanced Structure": 242,
    "Protoss Advanced Structure": 243,
    "Units": 244,
    "Workers": 245,
    "Cloakable Units": 246,
    "Burrowable Units": 247,
    "Replay (Play Button)": 248,
    "Replay (Pause Button)": 249,
}

DefaultButtonSet: TypeAlias = Literal[
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
    "Mojo" "Warbringer",
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
    "Cancel Order",
    "Cancel Place COP",
    "Building Is Constructed (Terran&Protoss)",
    "Rallyable Building Is Constructed (Terran&Protoss)",
    "Building Is Mutating (Zerg)",
    "Rallyable Building Is Mutating (Zerg)",
    "Cancel Infestation",
    "Cancel Mutation (Lair&Hive)",
    "Cancel Nuclear Strike",
    "Zerg Basic Mutation",
    "Terran Basic Structure",
    "Protoss Basic Structure",
    "Zerg Advanced Mutation",
    "Terran Advanced Structure",
    "Protoss Advanced Structure",
    "Units",
    "Workers",
    "Cloakable Units",
    "Burrowable Units",
    "Replay (Play Button)",
    "Replay (Pause Button)",
]