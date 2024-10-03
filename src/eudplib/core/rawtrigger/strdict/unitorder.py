from typing import Literal, TypeAlias

DefUnitOrderDict: dict[str, int] = {
    # Causes the unit to die. Normal units run the death iscript animation.
    "Die": 0,
    # while hallucinated units have the sound/sprite spawned and then are removed.
    # Normal unit stop command. Stops current order chain, and then goes to idle.
    "Stop": 1,
    "Guard": 2,  # Generic Guard order. Determines what guard command a unit uses.
    "Guard (Normal)": 2,
    "Guard (Player)": 3,  # Attacking Mobile unit guard order.
    "Guard (Subunit)": 4,  # Attacking unit turret guard.
    # Transport building guard. Set when a building picks up a unit.
    "Guard (Bunker)": 5,
    "Move": 6,  # Unit move. Ignores enemies on way to destination.
    "Ignore (Normal)": 6,
    "Reaver Stop": 7,  # Stop order for the reaver.
    "Stop (Reaver)": 7,
    "Attack": 8,  # Generic attack order.
    "Attack Obscured": 9,  # Move to attack shrouded building.
    "Attack Unit": 10,  # Mobile unit attacking a unit/building.
    "Attack Unit (Normal)": 10,
    "Attack In Range": 11,  # Attack for an immobile unit. Lurker attack.
    "Attack Ground (Unused)": 12,
    "Hover (Unused)": 13,
    "Attack Move": 14,  # Unit move, attack enemies along path to target.
    "Building Is Being Infested": 15,  # Ran when a unit is being infested.
    "Nothing 1 (Unused)": 16,  # Unknown
    "Power-Up (Unused)": 17,  # Unknown. Speculated to be a Powerup being built order
    "Guard (Building)": 18,  # Building tower guard.
    "Attack (Building)": 19,  # Building tower attack.
    "Script (Spider Mine)": 20,  # Spider mine idle order.
    "Stay In Range": 21,  # Mobile unit base attack.
    "Attack (Subunit)": 22,  # Mobile Unit Turret attack.
    "Nothing 2 (Normal)": 23,  # Do nothing, next order.
    # Unknown, used when a unit is changing state between siege <-> normal.
    "Nothing 3 (Unused)": 24,
    "Drone Start Build": 25,  # Move to target position and run drone build.
    "Drone Start Mutate": 25,
    "Drone Build": 26,  # Check resources and run drone land.
    "Drone Mutate": 26,
    "Cast Infest": 27,  # Move to Infest a unit.
    "Cast Spell (Infest 1)": 27,
    "Cast Infest Obscured": 28,  # Move to Infest shrouded unit
    "Cast Spell (Infest 2)": 28,
    # Infest Unit. Hides unit, runs infest 1 on target, then reshows unit.
    "Start Infest": 29,
    "Infest (Queen)": 29,
    "Build (SCV)": 30,  # Move/Start Terran Building.
    "Build (Probe)": 31,  # Full Protoss Building order.
    "Create Building (Probe)": 32,  # Creates the Protoss Building.
    "Is Building (SCV)": 33,  # SCV is building.
    "Repair Unit (SCV)": 34,  # Repair Unit.
    "Repair Unit Obscured (SCV)": 35,  # Move to repair shrouded building.
    "Place Add-On": 36,  # Move and start addon.
    "Build Add-On": 37,  # Building Addon.
    "Train": 38,  # Training Unit.
    "Train (Normal)": 38,
    # Rally to Visible Unit. Causes units to follow the selected unit.
    "Rally to Visible Unit": 39,
    "Rally to Ground Tile": 40,  # Rally to tile.
    "Zerg Birth": 41,  # Unit is being born.
    "Unit Morph": 42,  # Unit Morph
    "Building Morph": 43,  # Building Morph
    "Building Is Constructed (Terran)": 44,  # Terran Building, Is being built.
    "Zerg Build Self": 45,  # Zerg Building build order.
    "Build (Nydus Canal Exit)": 46,  # Nydus canal exit build order.
    "Enter (Nydus Canal)": 47,  # Enter/transport through nydus canal
    "Building Is Constructed (Protoss)": 48,  # Protoss Building being built order.
    # Move to/with unit or building. Causes units to load into transports
    "Follow": 49,  # or enter nydus canal or recharge shields.
    "Idle (Carrier)": 50,  # Idle command for the carrier.
    "Move (Carrier&Reaver)": 51,  # Carrier move command. Ignores enemies
    "Stop (Carrier)": 52,  # Carrier stop command. Runs idle.
    "Attack (Carrier)": 53,  # Generic Carrier attack command.
    "Attack Obscured (Carrier)": 54,  # Move to attack shrouded building.
    "Ignore 2 (Carrier)": 55,  # Unknown. Possibly a secondary move.
    "Attack Unit (Carrier)": 56,  # Carrier Attack Unit.
    "Hold Position (Carrier)": 57,  # Carrier Hold Position.
    "Idle (Reaver)": 58,  # Reaver Idle order.
    "Attack (Reaver)": 59,  # Generic reaver attack order.
    "Attack Obscured (Reaver)": 60,  # Move to attack shrouded building
    "Attack Unit (Reaver)": 61,  # Reaver attack unit.
    "Hold Position (Reaver)": 62,  # Reaver hold position.
    "Train Fighter": 63,  # Training subunit(scarab, interceptor).
    # Causes all interceptors within a carrier to be healed when not attacking.
    "Training (Subunit)": 63,
    "Move&Attack (Interceptor)": 64,  # Interceptor move and attack.
    "Move&Attack (Scarab)": 65,  # Scarab move and attack.
    "Recharge Shields (Unit)": 66,  # Unit recharge shields.
    # Shield Battery, recharge shield cast on unit or ground.
    # Unit runs Recharge Shields (Unit),
    # shield battery runs "Shield Battery Is Recharging".
    # If cast on ground, recharges all units within rechargeable radius.
    "Recharge Shields (Global)": 67,
    "Shield Battery Is Recharging": 68,  # Shield Battery, is recharging.
    "Return To Parent (Interceptor)": 69,  # Interceptor return to parent.
    "Land (Drone)": 70,  # Drone landing order. Used when building.
    "Land (Building)": 71,  # Building land order.
    "Lift Off (Building)": 72,  # Begin Building Liftoff
    "Lift Off (Drone)": 73,  # Begin Drone liftoff
    "Is Lifting Off": 74,  # Unit is lifting off.
    "Research Tech": 75,  # Building researching tech.
    "Is Researching Technology": 75,
    "Research Upgrade": 76,  # Building researching upgrade.
    "Is Performing Upgrade": 76,
    "Idle (Larva)": 77,  # Idle order for larva. Make sure it stays on creep,
    # dies if off, and says within the range of the parent it came from.
    "Is Spawning Larva": 78,  # Building is spawning larva.
    "Move to Harvest": 79,  # Generic move to harvest order.
    "Move to Harvest Obscured": 80,  # Move to harvest shrouded minerals/gas
    "Move to Harvest Gas": 81,  # Move to harvest gas.
    "Can Enter Gas Mine": 82,  # Check if it can enter the gas mine(no unit in it).
    "Enter/Exit Gas Mine": 83,  # Enter/exit mine, set return order.
    "Return Gas": 84,  # Return order, has gas.
    "Move to Harvest Minerals": 85,  # Move to harvest minerals.
    "Can Harvest Minerals": 86,  # Can harvest minerals(one unit per field).
    "Harvesting Minerals": 87,  # Harvesting minerals. Runs iscript to spawn weapon.
    "Harvesting Minerals Interrupted": 88,  # Harvesting minerals is interrupted.
    "Harvest 4 (Unknown)": 89,  # Unknown harvest command.
    "Return Minerals": 90,  # Return resources /B Has minerals.
    # Harvest Interrupt /B recharge shields.
    "Harvesting Interrupted - Recharge Shields": 91,
    "Move/Enter Transport": 92,  # Move/enter a transport.
    "Idle (Transport)": 93,  # Transport Idle command.
    "Load Unit (Mobile Transport)": 94,  # Mobile Transport unit pickup.
    "Load Unit (Bunker)": 95,  # Building pickup.
    "Load Unit (Unknown)": 96,  # Unknown /B AI pickup?
    "Idle (Power-Up)": 97,  # Idle for powerups.
    "Siege Mode": 98,  # Switch to Siege mode.
    "Tank Mode": 99,  # Switch to Tank mode.
    "Watch Target": 100,  # Immobile Unit base, watch the target.
    "Script (Starting Creep Growth)": 101,  # Start Spreading Creep.
    # Spreads creep. If it is a larva producer, runs that order also.
    "Script (Spread Creep&Spawn Larva)": 102,
    "Script (Stopping Creep Growth)": 103,  # Stops creep growth.
    "Guardian Aspect (Unused)": 104,  # Unused, Unit Morph is used for unit morphing.
    "Move and Merge Archon": 105,  # Move and start archon merge.
    "Move and Morph Archon": 105,
    "Completing Archon Summon": 106,  # Archon build self order.
    "Hold Position": 107,  # Attacking Unit hold position.
    "Hold Position (Normal)": 107,
    "Hold Position (Queen)": 108,  # Queen Hold position.
    "Cloak": 109,  # Cloak Unit.
    "Decloak": 110,  # Decloak Unit.
    "Unload": 111,  # Unload a unit from the transport.
    "Unload Unit (Transport)": 111,
    "Move and Unload": 112,  # Move to unload site and run unload order.
    "Move&Unload Unit (Transport)": 112,
    "Cast Yamato Gun": 113,  # Cast Spell: Yamato.
    "Cast Spell (Yamato Gun)": 113,
    "Cast Yamato Gun Obscured": 114,  # Move to cast spell on shrouded building.
    "Cast Spell On Obscured (Yamato Gun)": 114,
    "Cast Lockdown": 115,  # Cast Spell: Lockdown.
    "Cast Spell (Lockdown)": 115,
    "Burrow": 116,  # Burrow Unit.
    "Idle (Burrowed)": 117,  # Burrowed Unit idle.
    "Unburrow": 118,  # Unburrow unit.
    "Cast Dark Swarm": 119,  # Cast Spell: Dark Swarm.
    "Cast Spell (Dark Swarm)": 119,
    "Cast Parasite": 120,  # Cast Spell: Parasite.
    "Cast Spell (Parasite)": 120,
    "Cast Broodling": 121,  # Cast Spell: Spawn Broodings.
    "Cast Spell (Spawn Broodling)": 121,
    "Cast EMP Shockwave": 122,  # Cast Spell: EMP Shockwave.
    "Cast Spell (EMP Shockwave)": 122,
    "Nuke Wait": 123,  # Unknown.
    "Nuke Train": 124,  # Silo Idle
    "Idle (Nuclear Silo)": 124,
    "Nuke Launch": 125,  # Launch for nuclear missile.
    "Attack (Nuke)": 125,
    "Move&Paint Nuke Target": 126,  # Move to and set nuke target.
    "Attack Unit (Nuke)": 127,  # Nuke the ground location of the unit.
    "Attack Ground (Nuke)": 128,  # Nuke ground.
    "Nuke Track (Ghost)": 129,  # Ghost order during nuke.
    "Init Cloaking Field": 130,  # Run nearby cloaking.
    "Script (Cloak Nearby Units)": 130,
    "Cloaking Field": 131,  # Cloak non arbiters within range.
    "Cloak Nearby Units (Freezes the casting unit)": 131,
    "Place Spider Mine": 132,  # Place spider mine.
    "Right Click Action": 133,  # right click, sets correct order based on target.
    "Script (Right-Click Action)": 133,
    "Attack Unit (Infested Terran)": 134,  # Suicide Attack Unit.
    "Attack Ground (Infested Terran)": 135,  # Suicide Attack tile.
    "Hold Position (Suicide Units)": 136,  # Suicide Hold Position.
    "Cast Recall": 137,  # Recall(units within range of target pos).
    "Cast Spell (Recall)": 137,
    "Recall to Location": 138,  # Causes units to teleport when being recalled.
    "Teleport To Location (Freezes the casting unit)": 138,
    "Cast Scanner Sweep": 139,  # Place Scanner Sweep Unit at position.
    "Cast Spell (Scanner Sweep)": 139,
    "Idle (Scanner Sweep)": 140,  # Scanner Sweep Unit idle.
    "Cast Defensive Matrix": 141,  # Defensive Matrix cast on target.
    "Cast Spell (Defensive Matrix)": 141,
    "Cast Psionic Storm": 142,  # Cast Spell: Psi Storm.
    "Cast Spell (Psionic Storm)": 142,
    "Cast Irradiate": 143,  # Cast Spell: Irradiate.
    "Cast Spell (Irradiate)": 143,
    "Cast Plague": 144,  # Cast Spell: Plague.
    "Cast Spell (Plague)": 144,
    "Cast Consume": 145,  # Cast Spell: Consume.
    "Cast Spell (Consume)": 145,
    "Cast Ensnare": 146,  # Cast Spell: Ensnare.
    "Cast Spell (Ensnare)": 146,
    "Cast Stasis Field": 147,  # Cast Spell: Stasis Field.
    "Cast Spell (Stasis Field)": 147,
    "Cast Hallucination": 148,  # Hallucination Cast on target.
    "Cast Spell (Hallucination)": 148,
    "Kill Hallucination on Spell": 149,  # Kill Halluciation on spell cast.
    "Script (Hallucination)": 149,
    "Reset Collision (2 Units)": 150,  # Collision Reset between 2 units.
    # Collision reset between harvester and mine.
    "Reset Collision (Harvester&Mine)": 151,
    "Patrol": 152,  # Patrol to target, queue patrol to original position.
    "Patrol (Normal)": 152,
    "CTF COP (Initialize)": 153,  # CTF Initialization
    "Idle (CTF COP)": 154,  # CTF Idle
    "Unknown CTF COP 2": 155,  # Unknown? Reset COP?
    "Script (Computer)": 156,  # AI Control.
    "Attack Move (Computer)": 157,  # AI Attack Move?
    # Aggressive Attack Move? Units won't give up on a target.
    # If they see it, they will attack it, even worse than attack move.
    "Move (Harass)": 158,  # Might be a computer attack move?
    # Moves units to the center of the current area that they are at?
    # Not sure if the spacing is meant to allow for detectors to cover an area or not.  # noqa: E501
    "Patrol (Computer)": 159,
    "Guard Post": 160,  # Immobile Unit Guard.
    "Guard (Computer)": 160,
    "Rescuable Passive": 161,  # Rescuable unit idle.
    "Idle (Rescuable)": 161,
    "Idle (Neutral)": 162,  # Neutral Unit idle.
    # Return computer units to defensive position?
    # Was seen returning units that had followed a unit outside of a base and killed it.  # noqa: E501
    "Return To Base (Computer)": 163,
    "Init Psi Provider": 164,  # Adds to some kind of linked list.
    "Script (PSI Provider)": 164,
    "Self Destrucing": 165,  # Remove unit.
    "Fatal (Scarab)": 165,
    "Idle (Critter)": 166,  # Critter idle.
    "Hidden Trap": 167,  # Trap idle order.
    "Idle (Trap)": 167,
    "Open Door": 168,  # Opens the door.
    "Close Door": 169,  # Closes the door.
    "Hide Trap": 170,  # Trap return to idle.
    "Stop (Trap)": 170,
    "Reveal Trap": 171,  # Trap attack.
    "Attack (Trap)": 171,
    "Enable Doodad": 172,  # Enable Doodad State.
    "Disable Doodad": 173,  # Disable Doodad State.
    # Unused. Left over from unit warp in which now exists in Starcraft 2.
    "Warp In (Unused)": 174,
    "Idle (Medic)": 175,  # Idle command for the Terran Medic.
    "Cast Heal": 176,  # Heal cast on target.
    "Cast Spell (Heal)": 176,
    "Heal Move": 177,  # Attack move command for the Terran Medic.
    "Move (Medic)": 177,
    # Holds Position for Terran Medics, heals units within range.
    "Hold Position&Heal": 178,
    "Hold Position&Heal (Medic)": 178,
    "Return To Idle After Heal": 179,  # Return to idle after heal.
    "Cast Restoration": 180,  # Cast Spell: Restoration.
    "Cast Spell (Restoration)": 180,
    "Cast Disruption Web": 181,  # Cast Spell: Disruption Web.
    "Cast Spell (Disruption Web)": 181,
    "Cast Mind Control": 182,  # Mind Control Cast on Target.
    "Cast Spell (Mind Control)": 182,
    "Dark Archon Meld": 183,  # Dark Archon Meld.
    "Cast Feedback": 184,  # Feedback cast on target.
    "Cast Spell (Feedback)": 184,
    "Cast Optical Flare": 185,  # Cast Spell: Optical Flare.
    "Cast Spell (Optical Flare)": 185,
    "Cast Maelstrom": 186,  # Cast Spell: Maelstrom.
    "Cast Spell (Maelstrom)": 186,
    "Junk Yard Dog": 187,  # Junk yard dog movement.
    "Move (Junk Yard Dog)": 187,
    "Fatal": 188,  # Nothing.
}

DefaultUnitOrder: TypeAlias = Literal[
    "Die",
    "Stop",
    "Guard",
    "Guard (Player)",
    "Guard (Subunit)",
    "Guard (Bunker)",
    "Move",
    "Stop (Reaver)",
    "Attack",
    "Attack Obscured",
    "Attack Unit",
    "Attack In Range",
    "Attack Ground (Unused)",
    "Hover (Unused)",
    "Attack Move",
    "Building Is Being Infested",
    "Nothing 1 (Unused)",
    "Power-Up (Unused)",
    "Guard (Building)",
    "Attack (Building)",
    "Script (Spider Mine)",
    "Stay In Range",
    "Attack (Subunit)",
    "Nothing 2 (Normal)",
    "Nothing 3 (Unused)",
    "Drone Start Build",
    "Drone Build",
    "Cast Infest",
    "Cast Infest Obscured",
    "Start Infest",
    "Build (SCV)",
    "Build (Probe)",
    "Create Building (Probe)",
    "Is Building (SCV)",
    "Repair Unit (SCV)",
    "Repair Unit Obscured (SCV)",
    "Place Add-On",
    "Build Add-On",
    "Train",
    "Rally to Visible Unit",
    "Rally to Ground Tile",
    "Zerg Birth",
    "Unit Morph",
    "Building Morph",
    "Building Is Constructed (Terran)",
    "Zerg Build Self",
    "Build (Nydus Canal Exit)",
    "Enter (Nydus Canal)",
    "Building Is Constructed (Protoss)",
    "Follow",
    "Idle (Carrier)",
    "Move (Carrier&Reaver)",
    "Stop (Carrier)",
    "Attack (Carrier)",
    "Attack Obscured (Carrier)",
    "Ignore 2 (Carrier)",
    "Attack Unit (Carrier)",
    "Hold Position (Carrier)",
    "Idle (Reaver)",
    "Attack (Reaver)",
    "Attack Obscured (Reaver)",
    "Attack Unit (Reaver)",
    "Hold Position (Reaver)",
    "Train Fighter",
    "Move&Attack (Interceptor)",
    "Move&Attack (Scarab)",
    "Recharge Shields (Unit)",
    "Recharge Shields (Global)",
    "Shield Battery Is Recharging",
    "Return To Parent (Interceptor)",
    "Land (Drone)",
    "Land (Building)",
    "Lift Off (Building)",
    "Lift Off (Drone)",
    "Is Lifting Off",
    "Research Tech",
    "Research Upgrade",
    "Idle (Larva)",
    "Is Spawning Larva",
    "Move to Harvest",
    "Move to Harvest Obscured",
    "Move to Harvest Gas",
    "Can Enter Gas Mine",
    "Enter/Exit Gas Mine",
    "Return Gas",
    "Move to Harvest Minerals",
    "Can Harvest Minerals",
    "Harvesting Minerals",
    "Harvesting Minerals Interrupted",
    "Harvest 4 (Unknown)",
    "Return Minerals",
    "Harvesting Interrupted - Recharge Shields",
    "Move/Enter Transport",
    "Idle (Transport)",
    "Load Unit (Mobile Transport)",
    "Load Unit (Bunker)",
    "Load Unit (Unknown)",
    "Idle (Power-Up)",
    "Siege Mode",
    "Tank Mode",
    "Watch Target",
    "Script (Starting Creep Growth)",
    "Script (Spread Creep&Spawn Larva)",
    "Script (Stopping Creep Growth)",
    "Guardian Aspect (Unused)",
    "Move and Merge Archon",
    "Completing Archon Summon",
    "Hold Position",
    "Hold Position (Queen)",
    "Cloak",
    "Decloak",
    "Unload",
    "Move and Unload",
    "Cast Yamato Gun",
    "Cast Yamato Gun Obscured",
    "Cast Lockdown",
    "Burrow",
    "Idle (Burrowed)",
    "Unburrow",
    "Cast Dark Swarm",
    "Cast Parasite",
    "Cast Broodling",
    "Cast EMP Shockwave",
    "Nuke Wait",
    "Idle (Nuclear Silo)",
    "Nuke Launch",
    "Move&Paint Nuke Target",
    "Attack Unit (Nuke)",
    "Attack Ground (Nuke)",
    "Nuke Track (Ghost)",
    "Init Cloaking Field",
    "Cloaking Field",
    "Place Spider Mine",
    "Right Click Action",
    "Attack Unit (Infested Terran)",
    "Attack Ground (Infested Terran)",
    "Hold Position (Suicide Units)",
    "Cast Recall",
    "Recall to Location",
    "Cast Scanner Sweep",
    "Idle (Scanner Sweep)",
    "Cast Defensive Matrix",
    "Cast Psionic Storm",
    "Cast Irradiate",
    "Cast Plague",
    "Cast Consume",
    "Cast Ensnare",
    "Cast Stasis Field",
    "Cast Hallucination",
    "Kill Hallucination on Spell",
    "Reset Collision (2 Units)",
    "Reset Collision (Harvester&Mine)",
    "Patrol",
    "CTF COP (Initialize)",
    "Idle (CTF COP)",
    "Unknown CTF COP 2",
    "Script (Computer)",
    "Attack Move (Computer)",
    "Move (Harass)",
    "Patrol (Computer)",
    "Guard (Computer)",
    "Rescuable Passive",
    "Idle (Neutral)",
    "Return To Base (Computer)",
    "Init Psi Provider",
    "Fatal (Scarab)",
    "Idle (Critter)",
    "Hidden Trap",
    "Open Door",
    "Close Door",
    "Hide Trap",
    "Reveal Trap",
    "Enable Doodad",
    "Disable Doodad",
    "Warp In (Unused)",
    "Idle (Medic)",
    "Cast Heal",
    "Heal Move",
    "Hold Position&Heal",
    "Return To Idle After Heal",
    "Cast Restoration",
    "Cast Disruption Web",
    "Cast Mind Control",
    "Dark Archon Meld",
    "Cast Feedback",
    "Cast Optical Flare",
    "Cast Maelstrom",
    "Junk Yard Dog",
    "Fatal",
]
