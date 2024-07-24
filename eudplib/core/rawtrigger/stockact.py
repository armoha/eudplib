#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ...localize import _
from ...utils import EPD, ep_assert, ep_warn
from ..mapdata import UnitProperty
from .action import Action
from .constenc import (
    Add,
    AllyStatus,
    Byte,
    Count,
    Dword,
    EncodeAllyStatus,
    EncodeCount,
    EncodeModifier,
    EncodeOrder,
    EncodePlayer,
    EncodeProperty,
    EncodePropState,
    EncodeResource,
    EncodeScore,
    EncodeSwitchAction,
    Modifier,
    Player,
    PropState,
    Resource,
    Score,
    SwitchAction,
)
from .constenc import Order as _Order
from .strenc import (
    AIScript,
    EncodeAIScript,
    EncodeLocation,
    EncodeString,
    EncodeSwitch,
    EncodeUnit,
    Location,
    String,
    Switch,
    Unit,
)


def Victory() -> Action:  # noqa: N802
    """End scenario in victory for current player.

    The game ends in victory for the trigger's owner.
    Any players who are not executing a victory action are defeated.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 1, 0, 4)


def Defeat() -> Action:  # noqa: N802
    """End scenario in defeat for current player.

    This will end the scenario in defeat for the affected players.
    Any other players in the game will continue.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 2, 0, 4)


def PreserveTrigger() -> Action:  # noqa: N802
    """Preserve Trigger.

    Normally, a trigger will only run once for each owner.
    Triggers automatically disable themselves once they run through all of
    their actions, unless the Preserve Trigger action is present.
    If you want a trigger to remain in effect throughout the scenario,
    add the Preserve Trigger action to its action list.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 3, 0, 4)


def Wait(time: Dword) -> Action:  # noqa: N802
    """Wait for duration milliseconds.

    The wait action is used to delay other actions for the specified number of
    milliseconds. Because it is a blocking action, no other actions in the same
    trigger and no other blocking actions in other triggers will activate
    until it is done.
    """
    ep_warn(_("Don't use Wait action UNLESS YOU KNOW WHAT YOU'RE DOING!"))
    return Action(0, 0, 0, time, 0, 0, 0, 4, 0, 4)


def PauseGame() -> Action:  # noqa: N802
    """Pause the game.

    This action will put the game in a pause state.
    If a matching Unpause Game is not found, the program automatically unpauses
    the game when the current trigger is finished. Note that pause game has no
    effect in multiplayer scenarios or against computer controlled players.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 5, 0, 4)


def UnpauseGame() -> Action:  # noqa: N802
    """Unpause the game.

    This action resumes the game from a paused session.
    Note that this has no effect in multiplayer maps and will not effect any
    computer opponents in single player maps.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 6, 0, 4)


def Transmission(  # noqa: N802
    unit: Unit,
    where: Location,
    sound_name: String,
    time_modifier: Modifier,
    time: Dword,
    text: String,
    AlwaysDisplay: Byte = 4,  # noqa: N803
) -> Action:
    """Send transmission to current player from unit at location.

    A transmission is a combination of several different actions.
    First, you need to specify which unit at a location you want to send the
    transmission. This unit's portrait will be displayed for the duration of
    the transmission.
    You then need to select a WAV file to play, how long to animate the unit
    portrait, and what text message to display. The player receiving
    the transmission will receive a minimap ping when the transmission starts,
    and can press the space bar to center their screen on the unit sending the
    transmission.

    Note that this action has no effect on computer players,
    and it will prevent any other action (in the same trigger) from resuming
    until it has finished.
    """
    from ...epscript.epsimp import IsSCDBMap

    ep_assert(
        isinstance(AlwaysDisplay, int),
        _("AlwaysDisplay argument must be int, not '{}'").format(AlwaysDisplay),
    )
    if not IsSCDBMap():
        ep_warn(_("Don't use Wait action UNLESS YOU KNOW WHAT YOU'RE DOING!"))
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    sound_name = EncodeString(sound_name)
    modifier = EncodeModifier(time_modifier)
    text = EncodeString(text)
    return Action(where, text, sound_name, time, 0, 0, unit, 7, modifier, 4)


def PlayWAV(sound_name: String) -> Action:  # noqa: N802
    """Play WAV file.

    This will play a WAV file for the trigger's owner.
    """
    sound_name = EncodeString(sound_name)
    return Action(0, 0, sound_name, 0, 0, 0, 0, 8, 0, 4)


def DisplayText(text: String, AlwaysDisplay: Byte = 4) -> Action:  # noqa: N802, N803
    """Display for current player: text.

    Displays a specific text message to each owner of the condition.
    """
    ep_assert(
        isinstance(AlwaysDisplay, int),
        _("AlwaysDisplay argument must be int, not '{}'").format(AlwaysDisplay),
    )
    text = EncodeString(text)
    return Action(0, text, 0, 0, 0, 0, 0, 9, 0, 4)


def CenterView(where: Location) -> Action:  # noqa: N802
    """Center view for current player at location.

    This action creates the specified number of units at the specified Location
    If a unit is created 'Anywhere', it will appear in the center of the map.
    This action will not function while the game is paused.

    Keep in mind that when the conditions are successfully met,
    the unit(s) will be created for each player that owns the trigger.
    For example, if All Players own a trigger that creates a Terran Marine for
    Player 1, and the conditions of the trigger are true for four of the
    players, Player 1 will get 4 Marines.
    """
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, 0, 0, 0, 10, 0, 4)


def CreateUnitWithProperties(  # noqa: N802
    count: Byte,
    unit: Unit,
    where: Location,
    player: Player,
    properties: UnitProperty | bytes,
) -> Action:
    """Create quantity unit at location for player. Apply properties

    This action works just like Create Unit, except that you can customize
    the properties of the newly created unit(s).
    """
    if isinstance(Count, int):
        ep_assert(0 <= Count <= 255)
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    player = EncodePlayer(player)
    _property = EncodeProperty(properties)
    return Action(where, 0, 0, 0, player, _property, unit, 11, count, 28)


def SetMissionObjectives(text: String) -> Action:  # noqa: N802
    """Set Mission Objectives to: text.

    Changes the mission objectives text to something other than what was
    defined at the outset of the level. While this doesn't actually change the
    victory or defeat conditions for the scenario, it can be used to notify
    the players of changes to the scenario's objectives.
    """
    text = EncodeString(text)
    return Action(0, text, 0, 0, 0, 0, 0, 12, 0, 4)


def SetSwitch(switch: Switch, state: SwitchAction) -> Action:  # noqa: N802
    """Set switch.

    The set switch action can be used to:
    - Set a switch to its set position.
    - Clear a switch to its cleared position.
    - Toggle a switch: if a switch is cleared, it becomes set;
                       if it is set, it becomes cleared.
    - Randomly choose between the set or cleared position.
    """
    switch = EncodeSwitch(switch)
    state = EncodeSwitchAction(state)
    return Action(0, 0, 0, 0, 0, switch, 0, 13, state, 4)


def SetCountdownTimer(time_modifier: Modifier, time: Dword) -> Action:  # noqa: N802
    """Modify Countdown Timer: Set duration seconds.

    This allows you to set a countdown timer, in game seconds, which will
    appear at the top of the game screen and count down automatically.
    There is one countdown timer shared by all players. Any time the countdown
    timer is not equal to zero, it is displayed to all players.

    You can also use this action to add or subtract time from the countdown
    timer.
    """
    modifier = EncodeModifier(time_modifier)
    return Action(0, 0, 0, time, 0, 0, 0, 14, modifier, 4)


def RunAIScript(script: AIScript) -> Action:  # noqa: N802
    """Execute AI script script.

    This instructs the specified computer-controlled players to use a certain
    AI script. The AI script determines the overall aggressiveness and
    effectiveness of the computer player, and by changing the AI script during
    the scenario, you can effectively handicap the scenario.
    """
    script = EncodeAIScript(script)
    return Action(0, 0, 0, 0, 0, script, 0, 15, 0, 4)


def RunAIScriptAt(script: AIScript, where: Location) -> Action:  # noqa: N802
    """Execute AI script script at location.

    Identical to [Run AI Script](#link_action_runaiscript) but specifies
    a location to run the script at.
    Certain scripts are designed specifically to target a Location.
    """
    script = EncodeAIScript(script)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, 0, script, 0, 16, 0, 4)


def LeaderBoardControl(unit: Unit, label: String) -> Action:  # noqa: N802
    """Show Leader Board for most control of unit. Display label: label

    This will display the Leader Board to all players based on who controls
    the most of a particular unit in the scenario.
    """
    unit = EncodeUnit(unit)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, 0, unit, 17, 0, 20)


def LeaderBoardControlAt(  # noqa: N802
    unit: Unit, location: Location, label: String
) -> Action:
    """Show Leader Board for most control of units at location.

    Display label: label
    """
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    label = EncodeString(label)
    return Action(location, label, 0, 0, 0, 0, unit, 18, 0, 20)


def LeaderBoardResources(resource_type: Resource, label: String) -> Action:  # noqa: N802
    """Show Leader Board for accumulation of most resource.

    Display label: label
    This will display the Leader Board to all players based on who has
    the most resources.
    """
    resource_type = EncodeResource(resource_type)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, 0, resource_type, 19, 0, 4)


def LeaderBoardKills(unit: Unit, label: String) -> Action:  # noqa: N802
    """Show Leader Board for most kills of unit. Display label: label

    This will display the Leader Board to all players based on who has the most
    kills in the scenario.
    """
    unit = EncodeUnit(unit)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, 0, unit, 20, 0, 20)


def LeaderBoardScore(ScoreType: Score, label: String) -> Action:  # noqa: N803, N802
    """Show Leader Board for most points. Display label: label

    This will display the Leader Board to all players based on who has
    the most points.
    """
    score_type = EncodeScore(ScoreType)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, 0, score_type, 21, 0, 4)


def KillUnit(unit: Unit, player: Player) -> Action:  # noqa: N802
    """Kill all units for player.

    This action kills all units of a particular type for the player specified.
    This action has no effect while the game is paused.
    """
    unit = EncodeUnit(unit)
    player = EncodePlayer(player)
    return Action(0, 0, 0, 0, player, 0, unit, 22, 0, 20)


def KillUnitAt(  # noqa: N802
    count: Count, unit: Unit, where: Location, for_player: Player
) -> Action:
    """Kill quantity units for player at location.

    Similar to the 'Kill Unit' action, the 'Kill Unit at Location' action gives
    you the ability to kill a specified number of units of a particular type
    belonging to a certain player at the specified Location.
    This action will not function while the game is paused.
    """
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    for_player = EncodePlayer(for_player)
    return Action(where, 0, 0, 0, for_player, 0, unit, 23, count, 20)


def RemoveUnit(unit: Unit, player: Player) -> Action:  # noqa: N802
    """Remove all units for player.

    Remove Unit works just like Kill Unit, except that the affected units will
    simply disappear without actually dying.
    This action has no effect while the game is paused.
    """
    unit = EncodeUnit(unit)
    player = EncodePlayer(player)
    return Action(0, 0, 0, 0, player, 0, unit, 24, 0, 20)


def RemoveUnitAt(  # noqa: N802
    count: Count, unit: Unit, where: Location, for_player: Player
) -> Action:
    """Remove all units for player.

    This action works just like Remove Unit.
    In addition, you may specify a location and a quantity of units that the
    action will affect. It has no effect on a paused game.
    """
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    for_player = EncodePlayer(for_player)
    return Action(where, 0, 0, 0, for_player, 0, unit, 25, count, 20)


def SetResources(  # noqa: N802
    player: Player, modifier: Modifier, amount: Dword, resource_type: Resource
) -> Action:
    """Modify resources for player: Set quantity resource.

    The set resources action allows you to increase, decrease, or set
    the amount of resources that a player has.
    """
    player = EncodePlayer(player)
    modifier = EncodeModifier(modifier)
    resource_type = EncodeResource(resource_type)
    return Action(0, 0, 0, 0, player, amount, resource_type, 26, modifier, 4)


def SetScore(  # noqa: N802
    player: Player,
    modifier: Modifier,
    amount: Dword,
    ScoreType: Score,  # noqa: N803
) -> Action:
    """Modify score for player: Set quantity points.

    The set score action lets you the increase, decrease, or set the number of
    points that a player currently has.
    """
    player = EncodePlayer(player)
    modifier = EncodeModifier(modifier)
    score_type = EncodeScore(ScoreType)
    return Action(0, 0, 0, 0, player, amount, score_type, 27, modifier, 4)


def MinimapPing(where: Location) -> Action:  # noqa: N802
    """Show minimap ping for current player at location.

    This sends out a 'ping' on the mini map at the specified location.
    This can be used to draw attention to a particular spot or to track a
    moving location. Note that pressing the spacebar in the game after
    receiving the ping will not center your screen on the ping Location.
    Only transmissions allow you to jump to a different location with the
    spacebar.
    """
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, 0, 0, 0, 28, 0, 4)


def TalkingPortrait(unit: Unit, time: Dword) -> Action:  # noqa: N802
    """Show unit talking to current player for duration milliseconds.

    This will show the unit picture of your choice in the unit window in the
    game screen for the specified amount of time.
    """
    unit = EncodeUnit(unit)
    return Action(0, 0, 0, time, 0, 0, unit, 29, 0, 20)


def MuteUnitSpeech() -> Action:  # noqa: N802
    """Mute all non-trigger unit sounds for current player.

    This action will mute unit speech and set to half-volume all sound effects
    that the game normally produces, including music and combat sounds.
    This is particularly useful when you are playing a Transmission Action
    or any time you want to make sure a triggered sound is heard clearly.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 30, 0, 4)


def UnMuteUnitSpeech() -> Action:  # noqa: N802
    """Unmute all non-trigger unit sounds for current player.

    This action sets the sound effects for the game back to their original
    state.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 31, 0, 4)


def LeaderBoardComputerPlayers(state: PropState) -> Action:  # noqa: N802
    """Set use of computer players in leaderboard calculations.

    This action allows you to specify whether neutral, rescue and computer
    controlled players will be included in the leader board calculations.
    By default, all computer players are included in the tally.
    """
    state = EncodePropState(state)
    return Action(0, 0, 0, 0, 0, 0, 0, 32, state, 4)


def LeaderBoardGoalControl(goal: Dword, unit: Unit, label: String) -> Action:  # noqa: N802
    """Show Leader Board for player closest to control of number of unit.

    Display label: label
    This will display the Leader Board to all players based on the amount of
    units controlled on the map that are required to achieve a goal.
    In this type of leader board, the lower the number the better.
    """
    unit = EncodeUnit(unit)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, goal, unit, 33, 0, 20)


def LeaderBoardGoalControlAt(  # noqa: N802
    goal: Dword, unit: Unit, location: Location, label: String
) -> Action:
    """Show Leader Board for player closest to control of number of units at
    location.

    Display label: label
    This will display the Leader Board to all players based on the amount of
    units controlled at a certain Location that are required to achieve a goal.
    In this type of leader board, the lower the number the better.
    """
    unit = EncodeUnit(unit)
    location = EncodeLocation(location)
    label = EncodeString(label)
    return Action(location, label, 0, 0, 0, goal, unit, 34, 0, 20)


def LeaderBoardGoalResources(  # noqa: N802
    goal: Dword, resource_type: Resource, label: String
) -> Action:
    """Show Leader Board for player closest to accumulation of number resource.

    Display label: label
    This will display the Leader Board to all players based on who have
    the most resources required to achieve a goal.
    In this type of leader board, the lower the number the better.
    """
    resource_type = EncodeResource(resource_type)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, goal, resource_type, 35, 0, 4)


def LeaderBoardGoalKills(goal: Dword, unit: Unit, label: String) -> Action:  # noqa: N802
    """Show Leader Board for player closest to number kills of unit.

    Display label: label
    This will display the Leader Board to all players based on who have
    the most kills required to achieve a goal.
    In this type of leader board, the lower the number the better.
    """
    unit = EncodeUnit(unit)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, goal, unit, 36, 0, 20)


def LeaderBoardGoalScore(  # noqa: N802
    goal: Dword,
    ScoreType: Score,  # noqa: N803
    label: String,
) -> Action:
    """Show Leader Board for player closest to number points.

    Display label: label
    This will display the Leader Board to all players based on who have the
    most points required to achieve a goal.
    In this type of leader board, the lower the number the better.
    """
    score_type = EncodeScore(ScoreType)
    label = EncodeString(label)
    return Action(0, label, 0, 0, 0, goal, score_type, 37, 0, 4)


def MoveLocation(  # noqa: N802
    location: Location, on_unit: Unit, owner: Player, dest_location: Location
) -> Action:
    """Center location labeled location on units owned by player at location.

    This action will center a Location on a unit.
    In addition to choosing a location to move, you must specify a search
    location. The Action will ignore any units outside the search location.
    If no unit is found, the Location will move to the center of the search
    location. You can combine this Action with Center View to center the screen
    on a particular unit.
    """
    location = EncodeLocation(location)
    on_unit = EncodeUnit(on_unit)
    owner = EncodePlayer(owner)
    dest_loc = EncodeLocation(dest_location)
    return Action(dest_loc, 0, 0, 0, owner, location, on_unit, 38, 0, 20)


def MoveUnit(  # noqa: N802
    count: Count,
    unit_type: Unit,
    owner: Player,
    start_location: Location,
    dest_location: Location,
) -> Action:
    """Move quantity units for player at location to destination.

    This action will teleport a specified number of units (or unit) from one
    Location to another.
    """
    count = EncodeCount(count)
    unit = EncodeUnit(unit_type)
    owner = EncodePlayer(owner)
    start_loc = EncodeLocation(start_location)
    dest_loc = EncodeLocation(dest_location)
    return Action(start_loc, 0, 0, 0, owner, dest_loc, unit, 39, count, 20)


def LeaderBoardGreed(goal: Dword) -> Action:  # noqa: N802
    """Show Greed Leader Board for player closest to accumulation of number
    ore and gas.

    This will display the Leader Board to all players based on who is closest
    to reaching the goal of accumulating the most ore and gas.
    """
    return Action(0, 0, 0, 0, 0, goal, 0, 40, 0, 4)


def SetNextScenario(scenario_name: String) -> Action:  # noqa: N802
    """Load scenario after completion of current game.

    This trigger offers the ability to link multiple user-created maps together
    to form one large campaign.
    """
    scenario_name = EncodeString(scenario_name)
    return Action(0, scenario_name, 0, 0, 0, 0, 0, 41, 0, 4)


def SetDoodadState(  # noqa: N802
    state: PropState, unit: Unit, owner: Player, where: Location
) -> Action:
    """Set doodad state for units for player at location.

    The Installation tileset contains several doodads that can be enabled or
    disabled. The doors and concealed turrets can be set to start in one state
    or another by double clicking on them in the main window, but this action
    allows you to change their state during the course of the scenario. A
    location must be drawn around the doodads that you wish to affect with this
    action.

    Enabling a door closes it, and enabling a turret causes it to
    activate and attack any enemies of the trigger owner.
    """
    state = EncodePropState(state)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, 0, unit, 42, state, 20)


def SetInvincibility(  # noqa: N802
    state: PropState, unit: Unit, owner: Player, where: Location
) -> Action:
    """Set invincibility for units owned by player at location.

    This action makes the specified unit or units Invincible.
    Invincible units cannot be targeted or attacked, and take no damage.
    """
    state = EncodePropState(state)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, 0, unit, 43, state, 20)


def CreateUnit(  # noqa: N802
    number: Byte, unit: Unit, where: Location, for_player: Player
) -> Action:
    """Create quantity unit at location for player.

    This action creates the specified number of units at the specified
    Location. If a unit is created 'Anywhere', it will appear in the center of
    the map. This action will not function while the game is paused.

    Keep in mind that when the conditions are successfully met,
    the unit(s) will be created for each player that owns the trigger.
    For example, if **All Players** own a trigger that creates a Terran Marine
    for Player 1, and the conditions of the trigger are true for four of the
    players, Player 1 will get 4 Marines.
    """
    unit = EncodeUnit(unit)
    where = EncodeLocation(where)
    for_player = EncodePlayer(for_player)
    return Action(where, 0, 0, 0, for_player, 0, unit, 44, number, 20)


def SetDeaths(  # noqa: N802
    player: Player, modifier: Modifier, number: Dword, unit: Unit
) -> Action:
    """Modify death counts for player: Set quantity for unit.

    This will set the death counter of a particular unit, for the specified
    player, to a value listed in the action.
    """
    player = EncodePlayer(player)
    modifier = EncodeModifier(modifier)
    unit = EncodeUnit(unit)
    return Action(0, 0, 0, 0, player, number, unit, 45, modifier, 20)


def Order(  # noqa: N802
    unit: Unit,
    owner: Player,
    start_location: Location,
    order_type: _Order,
    dest_location: Location,
) -> Action:
    """Issue order to all units owned by player at location: order to
    destination.

    This action allows you to issue orders through a trigger to a unit
    (or units) that will change their behavior in a scenario.
    The different orders are attack, move and patrol.
    """
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    start_loc = EncodeLocation(start_location)
    order_type = EncodeOrder(order_type)
    dest_loc = EncodeLocation(dest_location)
    return Action(start_loc, 0, 0, 0, owner, dest_loc, unit, 46, order_type, 20)


def Comment(text: String) -> Action:  # noqa: N802
    """Comment: comment.

    If this action exists in a trigger, and is enabled, whatever text is listed
    in the text field will be displayed in the trigger text.
    If you disable this action, the normal trigger text will be displayed.
    """
    text = EncodeString(text)
    return Action(0, text, 0, 0, 0, 0, 0, 47, 0, 4)


def GiveUnits(  # noqa: N802
    count: Count, unit: Unit, owner: Player, where: Location, new_owner: Player
) -> Action:
    """Give quantity units owned by player at location to player.

    This action allows you to transfer units from one player to another.
    """
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    new_owner = EncodePlayer(new_owner)
    return Action(where, 0, 0, 0, owner, new_owner, unit, 48, count, 20)


def ModifyUnitHitPoints(  # noqa: N802
    count: Count, unit: Unit, owner: Player, where: Location, percent: Dword
) -> Action:
    """Set hit points for quantity units owned by player at location to
    percent%.

    This action will modify the specified unit(s) hit points. The hit points
    will be changed based on the percentage specified in the action trigger.
    """
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, percent, unit, 49, count, 20)


def ModifyUnitEnergy(  # noqa: N802
    count: Count, unit: Unit, owner: Player, where: Location, percent: Dword
) -> Action:
    """Set energy points for quantity units owned by player at location to
    percent%.

    This action will modify the specified unit(s) spell-casting energy. The
    energy will be changed based on the percentage specified in the action
    trigger.
    """
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, percent, unit, 50, count, 20)


def ModifyUnitShields(  # noqa: N802
    count: Count, unit: Unit, owner: Player, where: Location, percent: Dword
) -> Action:
    """Set shield points for quantity units owned by player at location to
    percent%.

    This action will modify the specified unit(s) shield points.
    The shield points will be changed based on the percentage specified in the
    action trigger.
    """
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, percent, unit, 51, count, 20)


def ModifyUnitResourceAmount(  # noqa: N802
    count: Count, owner: Player, where: Location, new_value: Dword
) -> Action:
    """Set resource amount for quantity resource sources owned by player at
    location to quantity.

    This action allows you to modify the amount of resources contained in the
    various mineral stores. For example, you could modify a Vespene Geyser
    so that it had 0 resources if you desire.
    """
    count = EncodeCount(count)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, new_value, 0, 52, count, 4)


def ModifyUnitHangarCount(  # noqa: N802
    add: Dword, count: Count, unit: Unit, owner: Player, where: Location
) -> Action:
    """Add at most quantity to hangar for quantity units at location owned by
    player.

    This action will modify the contents of a unit(s) hangar.
    For example, this will allow you to add 5 additional Interceptors to the
    Carrier's hangar.
    """
    count = EncodeCount(count)
    unit = EncodeUnit(unit)
    owner = EncodePlayer(owner)
    where = EncodeLocation(where)
    return Action(where, 0, 0, 0, owner, add, unit, 53, count, 20)


def PauseTimer() -> Action:  # noqa: N802
    """Pause the game.

    This action will put the game in a pause state.
    If a matching Unpause Game is not found, the program automatically unpauses
    the game when the current trigger is finished. Note that pause game has
    no effect in multiplayer scenarios or against computer controlled players.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 54, 0, 4)


def UnpauseTimer() -> Action:  # noqa: N802
    """Unpause the countdown timer.

    This action will resume the timer from a paused session.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 55, 0, 4)


def Draw() -> Action:  # noqa: N802
    """End the scenario in a draw for all players.

    This will end the scenario in a draw for the affected players.
    Any other players in the game will continue.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 56, 0, 4)


def SetAllianceStatus(player: Player, status: AllyStatus) -> Action:  # noqa: N802
    """Set Player to Ally status.

    This allows you to set the value of the affected players' alliance status.
    """
    player = EncodePlayer(player)
    ally = EncodeAllyStatus(status)
    return Action(0, 0, 0, 0, player, 0, ally, 57, 0, 4)


def SetMemory(dest: Dword, modtype: Modifier, value: Dword) -> Action:  # noqa: N802
    modifier = EncodeModifier(modtype)
    return Action(0, 0, 0, 0, EPD(dest), value, 0, 45, modifier, 20)


def SetMemoryEPD(dest: Dword, modtype: Modifier, value: Dword) -> Action:  # noqa: N802
    epd = EncodePlayer(dest)
    modifier = EncodeModifier(modtype)
    return Action(0, 0, 0, 0, epd, value, 0, 45, modifier, 20)


def SetNextPtr(trg: Dword, dest: Dword) -> Action:  # noqa: N802
    return SetMemory(trg + 4, 7, dest)


def SetDeathsX(  # noqa: N802
    player: Player, modifier: Modifier, number: Dword, unit: Unit, mask: Dword
) -> Action:
    player = EncodePlayer(player)
    modifier = EncodeModifier(modifier)
    unit = EncodeUnit(unit)
    return Action(mask, 0, 0, 0, player, number, unit, 45, modifier, 20, eudx=0x4353)


def SetMemoryX(  # noqa: N802
    dest: Dword, modtype: Modifier, value: Dword, mask: Dword
) -> Action:
    modifier = EncodeModifier(modtype)
    return SetDeathsX(EPD(dest), modifier, value, 0, mask)


def SetMemoryXEPD(  # noqa: N802
    epd: Dword, modtype: Modifier, value: Dword, mask: Dword
) -> Action:
    modifier = EncodeModifier(modtype)
    return SetDeathsX(epd, modifier, value, 0, mask)


def SetKills(  # noqa: N802
    player: Player, modifier: Modifier, number: Dword, unit: Unit
) -> Action | tuple[Action, Action, Action]:
    player = EncodePlayer(player)
    modifier = EncodeModifier(modifier)
    unit = EncodeUnit(unit)
    if isinstance(player, int) and player >= 12:
        if player == 13:
            return (
                SetMemory(0x6509B0, Add, -12 * 228),
                SetDeaths(13, modifier, number, unit),  # CurrentPlayer
                SetMemory(0x6509B0, Add, 12 * 228),
            )
        ep_assert(
            player <= 11,
            _("SetKills Player should be only P1~P12 or CurrentPlayer"),
        )
    if isinstance(unit, int):
        ep_assert(unit <= 227, _("SetKills Unit should be at most 227"))
    return SetDeaths(player - 228 * 12, modifier, number, unit)
