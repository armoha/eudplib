#!/usr/bin/python
# -*- coding: utf-8 -*-
DefUnitOrderDict: dict[str, int] = {
    "Die": 0,  # Causes the unit to die. Normal units run the death iscript animation,
    # while hallucinated units have the sound/sprite spawned and then are removed.
    "Stop": 1,  # Normal unit stop command. Stops current order chain, and then goes to idle.
    "Guard": 2,  # Generic Guard order. Determines what guard command a unit uses.
    "Guard (Normal)": 2,
    "Player Guard": 3,  # Attacking Mobile unit guard order.
    "Guard (Player)": 3,
    "Turret Guard": 4,  # Attacking unit turret guard.
    "Guard (Subunit)": 4,
    "Bunker Guard": 5,  # Transport building guard. Set when a building picks up a unit.
    "Guard (Bunker)": 5,
    "Move": 6,  # Unit move. Ignores enemies on way to destination.
    "Ignore (Normal)": 6,
    "Reaver Stop": 7,  # Stop order for the reaver.
    "Stop (Reaver)": 7,
    "Attack1": 8,  # Generic attack order.
    "Attack": 8,
    "Attack2": 9,  # Move to attack shrouded building.
    "Attack (Obscured)": 9,
    "Attack Unit": 10,  # Mobile unit attacking a unit/building.
    "Attack Unit (Normal)": 10,
    "Attack Fixed Range": 11,  # Attack for an immobile unit. Lurker attack.
    "Attack In Range": 11,
    "Attack Tile": 12,
    "Attack Ground (Unused)": 12,
    "Hover": 13,
    "Hover (Unused)": 13,
    "Attack Move": 14,  # Unit move, attack enemies along path to target.
    "Infest Mine 1": 15,  # Ran when a unit is being infested.
    "Building Is Being Infested": 15,
    "Nothing 1": 16,
    "Nothing 1 (Unused)": 16,
    "Powerup 1": 17,  # Unknown. Speculated to be a Powerup being built order.
    "Power-Up (Unused)": 17,
    "Tower Guard": 18,  # Building tower guard.
    "Guard (Building)": 18,
    "Tower Attack": 19,  # Building tower attack.
    "Attack (Building)": 19,
    "Vulture Mine": 20,  # Spidermine idle order.
    "Script (Spider Mine)": 20,
    "Stay In Range": 21,  # Mobile unit base attack.
    "Turret Attack": 22,  # Mobile Unit Turret attack.
    "Attack (Subunit)": 22,
    "Nothing 2": 23,  # Do nothing, next order.
    "Nothing 2 (Normal)": 23,
    "Nothing 3": 24,  # Unknown, used when a unit is changing state between siege <-> normal.
    "Nothing 3 (Unused)": 24,
    "Drone Start Build": 25,  # Move to target position and run drone build.
    "Drone Start Mutate": 25,
    "Drone Build": 26,  # Check resources and run drone land.
    "Drone Mutate": 26,
    "Infest Mine 2": 27,  # Move to Infest a unit.
    "Cast Spell (Infest 1)": 27,
    "Infest Mine 3": 28,  # Move to Infest shrouded unit
    "Cast Spell (Infest 2)": 28,
    "Infest Mine 4": 29,  # Infest Unit. Hides unit, runs infest 1 on target, then reshows unit.
    "Infest (Queen)": 29,
    "Build Terran": 30,  # Move/Start Terran Building.
    "Build (SCV)": 30,
    "Build Protoss 1": 31,  # Full Protoss Building order.
    "Build (Probe)": 31,
    "Build Protoss 2": 32,  # Creates the Protoss Building.
    "Create Building (Probe)": 32,
    "Constructing Building": 33,  # SCV is building.
    "Is Building (SCV)": 33,
    "Repair 1": 34,  # Repair Unit.
    "Repair Unit (SCV)": 34,
    "Repair 2": 35,  # Move to repair shrouded building.
    "Repair Unit (Obscured)": 35,
    "Place Add-On": 36,  # Move and start addon.
    "Build Add-On": 37,  # Building Addon.
    "Train": 38,  # Training Unit.
    "Train (Normal)": 38,
    "Rally Point 1": 39,  # Rally to Visible Unit. Causes units to follow the selected unit.
    "Rally to Visible Unit": 39,
    "Rally Point 2": 40,  # Rally to tile.
    "Rally to Ground Tile": 40,
    "Zerg Birth": 41,  # Unit is being born.
    "Morph 1": 42,  # Unit Morph
    "Unit Morph": 42,
    "Morph 2": 43,  # Building Morph
    "Building Morph": 43,
    "Build Self 1": 44,  # Terran Building, Is being built.
    "Building Is Constructed (Terran)": 44,
    "Zerg Build Self": 45,  # Zerg Building build order.
    "Build 5": 46,  # Nydus canal exit build order.
    "Build (Nydus Canal Exit)": 46,
    "Enter Nydus Canal": 47,  # Enter/transport through nydus canal
    "Enter (Nydus Canal)": 47,
    "Build Self 2": 48,  # Protoss Building being built order.
    "Building Is Constructed (Protoss)": 48,
    "Follow": 49,  # Move to/with unit or building. Causes units to load into transports
    # or enter nydus canal or recharge shields.
    "Carrier": 50,  # Idle command for the carrier.
    "Idle (Carrier)": 50,
    "Carrier Ignore 1": 51,  # Carrier move command. Ignores enemies
    "Move (Carrier&Reaver)": 51,
    "Carrier Stop": 52,  # Carrier stop command. Runs idle.
    "Stop (Carrier)": 52,
    "Carrier Attack 1": 53,  # Generic Carrier attack command.
    "Attack (Carrier)": 53,
    "Carrier Attack 2": 54,  # Move to attack shrouded building.
    "Attack Obscured (Carrier)": 54,
    "Carrier Ignore 2": 55,  # Unknown. Possibly a secondary move.
    "Ignore 2 (Carrier)": 55,
    "Carrier Fight": 56,  # Carrier Attack Unit.
    "Attack Unit (Carrier)": 56,
    "Carrier Hold": 57,  # Carrier Hold Position.
    "Hold Position 1": 57,
    "Hold Position (Carrier)": 57,
    "Reaver": 58,  # Reaver Idle order.
    "Idle (Reaver)": 58,
    "Reaver Attack 1": 59,  # Generic reaver attack order.
    "Attack (Reaver)": 59,
    "Reaver Attack 2": 60,  # Move to attack shrouded building
    "Attack Obscured (Reaver)": 60,
    "Reaver Fight": 61,  # Reaver attack unit.
    "Attack Unit (Reaver)": 61,
    "Reaver Hold": 62,  # Reaver hold position.
    "Hold Position (Reaver)": 62,
    "Train Fighter": 63,  # Training subunit(scarab, interceptor).
    # Causes all interceptors within a carrier to be healed when not attacking.
    "Training (Subunit)": 63,
    "Strafe Unit 1": 64,  # Interceptor move and attack.
    "Move&Attack (Interceptor)": 64,
    "Strafe Unit 2": 65,  # Scarab move and attack.
    "Move&Attack (Scarab)": 65,
    "Recharge Shields 1": 66,  # Unit recharge shields.
    "Recharge Shields (Unit)": 66,
    "Recharge Shields 2": 67,  # Shield Battery, recharge shield cast on unit or ground.
    # Unit runs recharge shields 1, shield battery runs shield battery.
    # If cast on ground, recharges all units within rechargeable radius.
    "Recharge Shields (Global)": 67,
    "Shield Battery": 68,  # Shield Battery, is recharging.
    "Shield Battery Is Recharging": 68,
    "Return": 69,  # Interceptor return to parent.
    "Return To Parent (Interceptor)": 69,
    "Drone Land": 70,  # Drone landing order. Used when building.
    "Land (Drone)": 70,
    "Building Land": 71,  # Building land order.
    "Land (Building)": 71,
    "Building Lift Off": 72,  # Begin Building Liftoff
    "Lift Off (Building)": 72,
    "Drone Lift Off": 73,  # Begin Drone liftoff
    "Lift Off (Drone)": 73,
    "Lift Off": 74,  # Unit is lifting off.
    "Is Lifting Off": 74,
    "Research Tech": 75,  # Building researching tech.
    "Is Researching Technology": 75,
    "Upgrade": 76,  # Building researching upgrade.
    "Is Performing Upgrade": 76,
    "Larva": 77,  # Idle order for larva. Make sure it stays on creep,
    # dies if off, and says within the range of the parent it came from.
    "Idle (Larva)": 77,
    "Spawning Larva": 78,  # Building is spawning larva.
    "Is Spawning Larva": 78,
    "Harvest 1": 79,  # Generic move to harvest order.
    "Move to Harvest": 79,
    "Harvest 2": 80,  # Move to harvest shrouded minerals/gas
    "Move to Harvest Obscured": 80,
    "Harvest Gas 1": 81,  # Move to harvest gas.
    "Move to Harvest Gas": 81,
    "Harvest Gas 2": 82,  # Check if it can enter the gas mine(no unit in it).
    "Can Enter Gas Mine": 82,
    "Harvest Gas 3": 83,  # Enter/exit mine, set return order.
    "Enter/Exit Gas Mine": 83,
    "Return Gas": 84,  # Return order, has gas.
    "Harvest Minerals 1": 85,  # Move to harvest minerals.
    "Move to Minerals": 85,
    "Move to Harvest Minerals": 85,
    "Harvest Minerals 2": 86,  # Can harvest minerals(one unit per field).
    "Can Harvest Minerals": 86,
    "Harvest Minerals 3": 87,  # Harvesting minerals. Runs iscript to spawn weapon.
    "Mining Minerals": 87,
    "Harvesting Minerals": 87,
    "Harvest 3": 88,  # Harvesting minerals is interrupted.
    "Harvesting Minerals Interrupted": 88,
    "Harvest 4": 89,  # Unknown harvest command.
    "Harvest 4 (Unknown)": 89,
    "Return Minerals": 90,  # Return resources /B Has minerals.
    "Harvest 5": 91,  # Harvest Interrupt /B recharge shields.
    "Harvesting Interrupted - Recharge Shields": 91,
    "Enter Transport": 92,  # Move/enter a transport.
    "Move/Enter Transport": 92,
    "Pick Up 1": 93,  # Transport Idle command.
    "Idle (Transport)": 93,
    "Pick Up 2": 94,  # Mobile Transport unit pickup.
    "Load Unit (Mobile Transport)": 94,
    "Pick Up 3": 95,  # Building pickup.
    "Load Unit (Bunker)": 95,
    "Pick Up 4": 96,  # Unknown /B AI pickup?
    "Load Unit (Unknown)": 96,
    "Powerup 2": 97,  # Idle for powerups.
    "Idle (Power-Up)": 97,
    "Siege Mode": 98,  # Switch to Siege mode.
    "Tank Mode": 99,  # Switch to Tank mode.
    "Watch Target": 100,  # Immobile Unit base, watch the target.
    "Initing Creep Growth": 101,  # Start Spreading Creep.
    "Script (Starting Creep Growth)": 101,
    "Spread Creep": 102,  # Spreads creep. If it is a larva producer, runs that order also.
    "Script (Spread Creep&Spawn Larva)": 102,
    "Stopping Creep Growth": 103,  # Stops creep growth.
    "Script (Stopping Creep Growth)": 103,
    "Guardian Aspect": 104,  # Unused, Morph 1 is used for unit morphing.
    "Guardian Aspect (Unused)": 104,
    "Warping Archon": 105,  # Move and start archon merge.
    "Move and Morph Archon": 105,
    "Completing Archon Summon": 106,  # Archon build self order.
    "Hold Position 2": 107,  # Attacking Unit hold position.
    "Hold Position (Normal)": 107,
    "Hold Position 3": 108,  # Queen Hold position.
    "Hold Position (Queen)": 108,
    "Cloak": 109,  # Cloak Unit.
    "Decloak": 110,  # Decloak Unit.
    "Unload": 111,  # Unload a unit from the transport.
    "Unload Unit (Transport)": 111,
    "Move Unload": 112,  # Move to unload site and run unload order.
    "Move&Unload Unit (Transport)": 112,
    "Fire Yamato Gun 1": 113,  # Cast Spell: Yamato.
    "Cast Spell (Yamato Gun)": 113,
    "Fire Yamato Gun 2": 114,  # Move to cast spell on shrouded building.
    "Cast Spell On Obscured (Yamato Gun)": 114,
    "Magna Pulse": 115,  # Cast Spell: Lockdown.
    "Cast Spell (Lockdown)": 115,
    "Burrow": 116,  # Burrow Unit.
    "Burrowed": 117,  # Burrowed Unit idle.
    "Idle (Burrowed)": 117,
    "Unburrow": 118,  # Unburrow unit.
    "Dark Swarm": 119,  # Cast Spell: Dark Swarm.
    "Cast Spell (Dark Swarm)": 119,
    "Cast Parasite": 120,  # Cast Spell: Parasite.
    "Cast Spell (Parasite)": 120,
    "Summon Broodlings": 121,  # Cast Spell: Spawn Broodings.
    "Cast Spell (Spawn Broodling)": 121,
    "EMP Shockwave": 122,  # Cast Spell: EMP Shockwave.
    "Cast Spell (EMP Shockwave)": 122,
    "Nuke Wait": 123,  # Unknown.
    "Unknown": 123,
    "Nuke Train": 124,  # Silo Idle
    "Idle (Nuclear Silo)": 124,
    "Nuke Launch": 125,  # Launch for nuclear missile.
    "Attack (Nuke)": 125,
    "Nuke Paint": 126,  # Move to and set nuke target.
    "Move&Paint Nuke Target": 126,
    "Nuke Unit": 127,  # Nuke the ground location of the unit.
    "Attack Unit (Nuke)": 127,
    "Nuke Ground": 128,  # Nuke ground.
    "Attack Ground (Nuke)": 128,
    "Nuke Track": 129,  # Ghost order during nuke.
    "Nuke Track (Ghost)": 129,
    "Initializing Arbiter": 130,  # Run nearby cloaking.
    "Script (Cloak Nearby Units)": 130,
    "Cloaking nearby units": 131,  # Cloak non arbiters within range.
    "Cloak Nearby Units (Freezes the casting unit)": 131,
    "Place Mine": 132,  # Place spider mine.
    "Place Spider Mine": 132,
    "Right Click Action": 133,  # right click, sets correct order based on target.
    "Script (Right-Click Action)": 133,
    "Sap Unit": 134,  # Suicide Attack Unit.
    "Attack Unit (Infested Terran)": 134,
    "Sap Location": 135,  # Suicide Attack tile.
    "Attack Ground (Infested Terran)": 135,
    "Hold Position 4": 136,  # Suicide Hold Position.
    "Hold Position (Suicide Units)": 136,
    "Teleport": 137,  # Recall(units within range of target pos).
    "Cast Spell (Recall)": 137,
    "Teleport to Location": 138,  # Causes units to teleport when being recalled.
    "Teleport To Location (Freezes the casting unit)": 138,
    "Place Scanner": 139,  # Place Scanner Sweep Unit at position.
    "Cast Spell (Scanner Sweep)": 139,
    "Scanner": 140,  # Scanner Sweep Unit idle.
    "Idle (Scanner Sweep)": 140,
    "Defensive Matrix": 141,  # Defensive Matrix cast on target.
    "Cast Spell (Defensive Matrix)": 141,
    "Psionic Storm": 142,  # Cast Spell: Psi Storm.
    "Cast Spell (Psionic Storm)": 142,
    "Irradiate": 143,  # Cast Spell: Irradiate.
    "Cast Spell (Irradiate)": 143,
    "Plague": 144,  # Cast Spell: Plague.
    "Cast Spell (Plague)": 144,
    "Consume": 145,  # Cast Spell: Consume.
    "Cast Spell (Consume)": 145,
    "Ensnare": 146,  # Cast Spell: Ensnare.
    "Cast Spell (Ensnare)": 146,
    "Stasis Field": 147,  # Cast Spell: Stasis Field.
    "Cast Spell (Stasis Field)": 147,
    "Hallucination 1": 148,  # Hallucination Cast on target.
    "Cast Spell (Hallucination)": 148,
    "Hallucination 2": 149,  # Kill Halluciation on spell cast.
    "Script (Hallucination)": 149,
    "Reset Collision 1": 150,  # Collision Reset between 2 units.
    "Reset Collision (2 Units)": 150,
    "Reset Collision 2": 151,  # Collision reset between harvester and mine.
    "Reset Collision (Harvester&Mine)": 151,
    "Patrol": 152,  # Patrol to target, queue patrol to original position.
    "Patrol (Normal)": 152,
    "CTF COP Init": 153,  # CTF Initialization
    "CTF COP (Initialize)": 153,
    "CTF COP 1": 154,  # CTF Idle
    "Idle (CTF COP)": 154,
    "CTF COP 2": 155,  # Unknown? Reset COP?
    "Unknown CTF COP 2": 155,
    "Computer AI": 156,  # AI Control.
    "Script (Computer)": 156,
    "Atk Move EP": 157,  # AI Attack Move?
    "Attack Move (Computer)": 157,
    "Harass Move": 158,  # Aggressive Attack Move? Units won't give up on a target.
    # If they see it, they will attack it, even worse than attack move. Might be a computer attack move?
    "Move (Harass)": 158,
    "AI Patrol": 159,  # Moves units to the center of the current area that they are at?
    # Not sure if the spacing is meant to allow for detectors to cover an area or not.
    "Patrol (Computer)": 159,
    "Guard Post": 160,  # Immobile Unit Guard.
    "Guard (Computer)": 160,
    "Rescuable Passive": 161,  # Rescuable unit idle.
    "Idle (Rescuable)": 161,
    "Neutral": 162,  # Neutral Unit idle.
    "Idle (Neutral)": 162,
    "Computer Return": 163,  # Return computer units to defensive position?
    # Was seen returning units that had followed a unit outside of a base and killed it.
    "Return To Base (Computer)": 163,
    "Initing Psi Provider": 164,  # Init Psi Provider. Adds to some kind of linked list.
    "Script (PSI Provider)": 164,
    "Self Destrucing": 165,  # Remove unit.
    "Fatal (Scarab)": 165,
    "Critter": 166,  # Critter idle.
    "Idle (Critter)": 166,
    "Hidden Gun": 167,  # Trap idle order.
    "Idle (Trap)": 167,
    "Open Door": 168,  # Opens the door.
    "Close Door": 169,  # Closes the door.
    "Hide Trap": 170,  # Trap return to idle.
    "Stop (Trap)": 170,
    "Reveal Trap": 171,  # Trap attack.
    "Attack (Trap)": 171,
    "Enable Doodad": 172,  # Enable Doodad State.
    "Disable Doodad": 173,  # Disable Doodad State.
    "Warp In": 174,  # Unused. Left over from unit warp in which now exists in Starcraft 2.
    "Warp In (Unused)": 174,
    "Medic": 175,  # Idle command for the Terran Medic.
    "Idle (Medic)": 175,
    "Medic Heal 1": 176,  # Heal cast on target.
    "Cast Spell (Heal)": 176,
    "Heal Move": 177,  # Attack move command for the Terran Medic.
    "Move (Medic)": 177,
    "Medic Hold Position": 178,  # Holds Position for Terran Medics, heals units within range.
    "Hold Position&Heal (Medic)": 178,
    "Medic Heal 2": 179,  # Return to idle after heal.
    "Return To Idle After Heal": 179,
    "Restoration": 180,  # Cast Spell: Restoration.
    "Cast Spell (Restoration)": 180,
    "Cast Disruption Web": 181,  # Cast Spell: Disruption Web.
    "Cast Spell (Disruption Web)": 181,
    "Cast Mind Control": 182,  # Mind Control Cast on Target.
    "Cast Spell (Mind Control)": 182,
    "Warping Dark Archon": 183,  # Dark Archon Meld.
    "Dark Archon Meld": 183,
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
