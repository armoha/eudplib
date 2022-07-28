#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from .action import Action
from .constenc import (
    Add,
    CurrentPlayer,
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
)
from .strenc import (
    EncodeAIScript,
    EncodeLocation,
    EncodeString,
    EncodeSwitch,
    EncodeUnit,
)
from ...localize import _
from ...utils import EPD, ep_warn, ep_assert, unProxy


def Victory():
    """End scenario in victory for current player.

    The game ends in victory for the trigger’s owner. Any players who are not executing a victory action are defeated.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 1, 0, 4)


def Defeat():
    """End scenario in defeat for current player.

    This will end the scenario in defeat for the affected players. Any other players in the game will continue.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 2, 0, 4)


def PreserveTrigger():
    """Preserve Trigger.

    Normally, a trigger will only run once for each owner. Triggers automatically disable themselves once they run through all of their actions, unless the Preserve Trigger action is present. If you want a trigger to remain in effect throughout the scenario, add the Preserve Trigger action to its action list.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 3, 0, 4)


def Wait(Time):
    """Wait for duration milliseconds.

    The wait action is used to delay other actions for the specified number of milliseconds. Because it is a blocking action, no other actions in the same trigger and no other blocking actions in other triggers will activate until it is done.
    """
    ep_warn(_("Don't use Wait action UNLESS YOU KNOW WHAT YOU'RE DOING!"))
    return Action(0, 0, 0, Time, 0, 0, 0, 4, 0, 4)


def PauseGame():
    """Pause the game.

    This action will put the game in a pause state. If a matching Unpause Game is not found, the program automatically unpauses the game when the current trigger is finished. Note that pause game has no effect in multiplayer scenarios or against computer controlled players.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 5, 0, 4)


def UnpauseGame():
    """Unpause the game.

    This action resumes the game from a paused session. Note that this has no effect in multiplayer maps and will not effect any computer opponents in single player maps.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 6, 0, 4)


def Transmission(Unit, Where, WAVName, TimeModifier, Time, Text, AlwaysDisplay=4):
    """Send transmission to current player from unit at location.

    A transmission is a combination of several different actions. First, you need to specify which unit at a location you want to send the transmission. This unit’s portrait will be displayed for the duration of the transmission. You then need to select a WAV file to play, how long to animate the unit portrait, and what text message to display for players that have Subtitles turned on. The player receiving the transmission will receive a minimap ping when the transmission starts, and can press the space bar to center their screen on the unit sending the transmission.

    Note that this action has no effect on computer players, and it will prevent any other action (in the same trigger) from resuming until it has finished.
    """
    from ...epscript import IsSCDBMap

    if not IsSCDBMap:
        ep_warn(_("Don't use Wait action UNLESS YOU KNOW WHAT YOU'RE DOING!"))
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    WAVName = EncodeString(WAVName, issueError=True)
    TimeModifier = EncodeModifier(TimeModifier, issueError=True)
    Text = EncodeString(Text, issueError=True)
    return Action(
        Where, Text, WAVName, Time, 0, 0, Unit, 7, TimeModifier, AlwaysDisplay
    )


def PlayWAV(WAVName):
    """Play WAV file.

    This will play a WAV file for the trigger’s owner.
    """
    WAVName = EncodeString(WAVName, issueError=True)
    return Action(0, 0, WAVName, 0, 0, 0, 0, 8, 0, 4)


def DisplayText(Text, AlwaysDisplay=4):
    """Display for current player: text.

    Displays a specific text message to each owner of the condition. Text messages will only appear if the affected player has Subtitles turned on in the Starcraft Sound Options Menu or if the Always Display option is checked for the action.
    """
    Text = EncodeString(Text, issueError=True)
    return Action(0, Text, 0, 0, 0, 0, 0, 9, 0, AlwaysDisplay)


def CenterView(Where):
    """Center view for current player at location.

    This action creates the specified number of units at the specified Location. If a unit is created ‘Anywhere’, it will appear in the center of the map. This action will not function while the game is paused.

    Keep in mind that when the conditions are successfully met, the unit(s) will be created for each player that owns the trigger. For example, if All Players own a trigger that creates a Terran Marine for Player 1, and the conditions of the trigger are true for four of the players, Player 1 will get 4 Marines.

    """
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, 0, 0, 0, 10, 0, 4)


def CreateUnitWithProperties(Count, Unit, Where, Player, Properties):
    """Create quantity unit at location for player. Apply properties

    This action works just like Create Unit, except that you can customize the properties of the newly created unit(s).
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    Player = EncodePlayer(Player, issueError=True)
    Properties = EncodeProperty(Properties, issueError=True)
    return Action(Where, 0, 0, 0, Player, Properties, Unit, 11, Count, 28)


def SetMissionObjectives(Text):
    """Set Mission Objectives to: text.

    Changes the mission objectives text to something other than what was defined at the outset of the level. While this doesn’t actually change the victory or defeat conditions for the scenario, it can be used to notify the players of changes to the scenario’s objectives.
    """
    Text = EncodeString(Text, issueError=True)
    return Action(0, Text, 0, 0, 0, 0, 0, 12, 0, 4)


def SetSwitch(Switch, State):
    """Set switch.

    The set switch action can be used to:

    -   Set a switch to its set position.
    -   Clear a switch to its cleared position.
    -   Toggle a switch: if a switch is cleared, it becomes set; if it is set, it becomes cleared.
    -   Randomly choose between the set or cleared position.
    """
    Switch = EncodeSwitch(Switch, issueError=True)
    State = EncodeSwitchAction(State, issueError=True)
    return Action(0, 0, 0, 0, 0, Switch, 0, 13, State, 4)


def SetCountdownTimer(TimeModifier, Time):
    """Modify Countdown Timer: Set duration seconds.

    This allows you to set a countdown timer, in game seconds, which will appear at the top of the game screen and count down automatically. There is one countdown timer shared by all players. Any time the countdown timer is not equal to zero, it is displayed to all players.

    You can also use this action to add or subtract time from the countdown timer.
    """
    TimeModifier = EncodeModifier(TimeModifier, issueError=True)
    return Action(0, 0, 0, Time, 0, 0, 0, 14, TimeModifier, 4)


def RunAIScript(Script):
    """Execute AI script script.

    This instructs the specified computer-controlled players to use a certain AI script. The AI script determines the overall aggressiveness and effectiveness of the computer player, and by changing the AI script during the scenario, you can effectively handicap the scenario.
    """
    Script = EncodeAIScript(Script, issueError=True)
    return Action(0, 0, 0, 0, 0, Script, 0, 15, 0, 4)


def RunAIScriptAt(Script, Where):
    """Execute AI script script at location.

    Identical to [Run AI Script](#link_action_runaiscript) but specifies a location to run the script at. Certain scripts are designed specifically to target a Location.
    """
    Script = EncodeAIScript(Script, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, 0, Script, 0, 16, 0, 4)


def LeaderBoardControl(Unit, Label):
    """Show Leader Board for most control of unit. Display label: label

    This will display the Leader Board to all players based on who controls the most of a particular unit in the scenario.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, Unit, 17, 0, 20)


def LeaderBoardControlAt(Unit, Location, Label):
    """Show Leader Board for most control of units at location. Display label: label"""
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(Location, Label, 0, 0, 0, 0, Unit, 18, 0, 20)


def LeaderBoardResources(ResourceType, Label):
    """Show Leader Board for accumulation of most resource. Display label: label

    This will display the Leader Board to all players based on who has the most resources.
    """
    ResourceType = EncodeResource(ResourceType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, ResourceType, 19, 0, 4)


def LeaderBoardKills(Unit, Label):
    """Show Leader Board for most kills of unit. Display label: label

    This will display the Leader Board to all players based on who has the most kills in the scenario.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, Unit, 20, 0, 20)


def LeaderBoardScore(ScoreType, Label):
    """Show Leader Board for most points. Display label: label

    This will display the Leader Board to all players based on who has the most points.
    """
    ScoreType = EncodeScore(ScoreType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, 0, ScoreType, 21, 0, 4)


def KillUnit(Unit, Player):
    """Kill all units for player.

    This action kills all units of a particular type for the player specified. This action has no effect while the game is paused.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Player = EncodePlayer(Player, issueError=True)
    return Action(0, 0, 0, 0, Player, 0, Unit, 22, 0, 20)


def KillUnitAt(Count, Unit, Where, ForPlayer):
    """Kill quantity units for player at location.

    Similar to the ‘Kill Unit’ action, the ‘Kill Unit at Location’ action gives you the ability to kill a specified number of units of a particular type belonging to a certain player at the specified Location. This action will not function while the game is paused.
    """
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    ForPlayer = EncodePlayer(ForPlayer, issueError=True)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 23, Count, 20)


def RemoveUnit(Unit, Player):
    """Remove all units for player.

    Remove Unit works just like Kill Unit, except that the affected units will simply disappear without actually dying. This action has no effect while the game is paused.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Player = EncodePlayer(Player, issueError=True)
    return Action(0, 0, 0, 0, Player, 0, Unit, 24, 0, 20)


def RemoveUnitAt(Count, Unit, Where, ForPlayer):
    """Remove all units for player.

    This action works just like Remove Unit. In addition, you may specify a location and a quantity of units that the action will affect. It has no effect on a paused game.
    """
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    ForPlayer = EncodePlayer(ForPlayer, issueError=True)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 25, Count, 20)


def SetResources(Player, Modifier, Amount, ResourceType):
    """Modify resources for player: Set quantity resource.

    The set resources action allows you to increase, decrease, or set the amount of resources that a player has.
    """
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    ResourceType = EncodeResource(ResourceType, issueError=True)
    return Action(0, 0, 0, 0, Player, Amount, ResourceType, 26, Modifier, 4)


def SetScore(Player, Modifier, Amount, ScoreType):
    """Modify score for player: Set quantity points.

    The set score action lets you the increase, decrease, or set the number of points that a player currently has.
    """
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    ScoreType = EncodeScore(ScoreType, issueError=True)
    return Action(0, 0, 0, 0, Player, Amount, ScoreType, 27, Modifier, 4)


def MinimapPing(Where):
    """Show minimap ping for current player at location.

    This sends out a ‘ping’ on the mini map at the specified location. This can be used to draw attention to a particular spot or to track a moving location. Note that pressing the spacebar in the game after receiving the ping will not center your screen on the ping Location. Only transmissions allow you to jump to a different location with the spacebar.
    """
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, 0, 0, 0, 28, 0, 4)


def TalkingPortrait(Unit, Time):
    """Show unit talking to current player for duration milliseconds.

    This will show the unit picture of your choice in the unit window in the game screen for the specified amount of time.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    return Action(0, 0, 0, Time, 0, 0, Unit, 29, 0, 20)


def MuteUnitSpeech():
    """Mute all non-trigger unit sounds for current player.

    This action will mute unit speech and set to half-volume all sound effects that the game normally produces, including music and combat sounds. This is particularly useful when you are playing a Transmission Action or any time you want to make sure a triggered sound is heard clearly.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 30, 0, 4)


def UnMuteUnitSpeech():
    """Unmute all non-trigger unit sounds for current player.

    This action sets the sound effects for the game back to their original state.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 31, 0, 4)


def LeaderBoardComputerPlayers(State):
    """Set use of computer players in leaderboard calculations.

    This action allows you to specify whether neutral, rescue and computer controlled players will be included in the leader board calculations. By default, all computer players are included in the tally.
    """
    State = EncodePropState(State, issueError=True)
    return Action(0, 0, 0, 0, 0, 0, 0, 32, State, 4)


def LeaderBoardGoalControl(Goal, Unit, Label):
    """Show Leader Board for player closest to control of number of unit. Display label: label

    This will display the Leader Board to all players based on the amount of units controlled on the map that are required to achieve a goal. In this type of leader board, the lower the number the better.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 33, 0, 20)


def LeaderBoardGoalControlAt(Goal, Unit, Location, Label):
    """Show Leader Board for player closest to control of number of units at location. Display label: label

    This will display the Leader Board to all players based on the amount of units controlled at a certain Location that are required to achieve a goal. In this type of leader board, the lower the number the better.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Location = EncodeLocation(Location, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(Location, Label, 0, 0, 0, Goal, Unit, 34, 0, 20)


def LeaderBoardGoalResources(Goal, ResourceType, Label):
    """Show Leader Board for player closest to accumulation of number resource. Display label: label

    This will display the Leader Board to all players based on who have the most resources required to achieve a goal. In this type of leader board, the lower the number the better.
    """
    ResourceType = EncodeResource(ResourceType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, ResourceType, 35, 0, 4)


def LeaderBoardGoalKills(Goal, Unit, Label):
    """Show Leader Board for player closest to number kills of unit. Display label: label

    This will display the Leader Board to all players based on who have the most kills required to achieve a goal. In this type of leader board, the lower the number the better.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, Unit, 36, 0, 20)


def LeaderBoardGoalScore(Goal, ScoreType, Label):
    """Show Leader Board for player closest to number points. Display label: label

    This will display the Leader Board to all players based on who have the most points required to achieve a goal. In this type of leader board, the lower the number the better.
    """
    ScoreType = EncodeScore(ScoreType, issueError=True)
    Label = EncodeString(Label, issueError=True)
    return Action(0, Label, 0, 0, 0, Goal, ScoreType, 37, 0, 4)


def MoveLocation(Location, OnUnit, Owner, DestLocation):
    """Center location labeled location on units owned by player at location.

    This action will center a Location on a unit. In addition to choosing a location to move, you must specify a search location. The Action will ignore any units outside the search location. If no unit is found, the Location will move to the center of the search location. You can combine this Action with Center View to center the screen on a particular unit.
    """
    Location = EncodeLocation(Location, issueError=True)
    OnUnit = EncodeUnit(OnUnit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    DestLocation = EncodeLocation(DestLocation, issueError=True)
    return Action(DestLocation, 0, 0, 0, Owner, Location, OnUnit, 38, 0, 20)


def MoveUnit(Count, UnitType, Owner, StartLocation, DestLocation):
    """Move quantity units for player at location to destination.

    This action will teleport a specified number of units (or unit) from one Location to another.
    """
    Count = EncodeCount(Count, issueError=True)
    UnitType = EncodeUnit(UnitType, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    StartLocation = EncodeLocation(StartLocation, issueError=True)
    DestLocation = EncodeLocation(DestLocation, issueError=True)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, UnitType, 39, Count, 20)


def LeaderBoardGreed(Goal):
    """Show Greed Leader Board for player closest to accumulation of number ore and gas.

    This will display the Leader Board to all players based on who is closest to reaching the goal of accumulating the most ore and gas.
    """
    return Action(0, 0, 0, 0, 0, Goal, 0, 40, 0, 4)


def SetNextScenario(ScenarioName):
    """Load scenario after completion of current game.

    This trigger offers the ability to link multiple user-created maps together to form one large campaign.
    """
    ScenarioName = EncodeString(ScenarioName, issueError=True)
    return Action(0, ScenarioName, 0, 0, 0, 0, 0, 41, 0, 4)


def SetDoodadState(State, Unit, Owner, Where):
    """Set doodad state for units for player at location.

    The Installation tileset contains several doodads that can be enabled or disabled. The doors and concealed turrets can be set to start in one state or another by double clicking on them in the main window, but this action allows you to change their state during the course of the scenario. A location must be drawn around the doodads that you wish to affect with this action.

    Enabling a door closes it, and enabling a turret causes it to activate and attack any enemies of the trigger owner.
    """
    State = EncodePropState(State, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 42, State, 20)


def SetInvincibility(State, Unit, Owner, Where):
    """Set invincibility for units owned by player at location.

    This action makes the specified unit or units Invincible. Invincible units cannot be targeted or attacked, and take no damage.
    """
    State = EncodePropState(State, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, 0, Unit, 43, State, 20)


def CreateUnit(Number, Unit, Where, ForPlayer):
    """Create quantity unit at location for player.

    This action creates the specified number of units at the specified Location. If a unit is created ‘Anywhere’, it will appear in the center of the map. This action will not function while the game is paused.

    Keep in mind that when the conditions are successfully met, the unit(s) will be created for each player that owns the trigger. For example, if **All Players** own a trigger that creates a Terran Marine for Player 1, and the conditions of the trigger are true for four of the players, Player 1 will get 4 Marines.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    ForPlayer = EncodePlayer(ForPlayer, issueError=True)
    return Action(Where, 0, 0, 0, ForPlayer, 0, Unit, 44, Number, 20)


def SetDeaths(Player, Modifier, Number, Unit):
    """Modify death counts for player: Set quantity for unit.

    This will set the death counter of a particular unit, for the specified player, to a value listed in the action.
    """
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Action(0, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20)


def Order(Unit, Owner, StartLocation, OrderType, DestLocation):
    """Issue order to all units owned by player at location: order to destination.

    This action allows you to issue orders through a trigger to a unit (or units) that will change their behavior in a scenario. The different orders are attack, move and patrol.
    """
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    StartLocation = EncodeLocation(StartLocation, issueError=True)
    OrderType = EncodeOrder(OrderType, issueError=True)
    DestLocation = EncodeLocation(DestLocation, issueError=True)
    return Action(StartLocation, 0, 0, 0, Owner, DestLocation, Unit, 46, OrderType, 20)


def Comment(Text):
    """Comment: comment.

    If this action exists in a trigger, and is enabled, whatever text is listed in the text field will be displayed in the trigger text. If you disable this action, the normal trigger text will be displayed.
    """
    Text = EncodeString(Text, issueError=True)
    return Action(0, Text, 0, 0, 0, 0, 0, 47, 0, 4)


def GiveUnits(Count, Unit, Owner, Where, NewOwner):
    """Give quantity units owned by player at location to player.

    This action allows you to transfer units from one player to another.
    """
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    NewOwner = EncodePlayer(NewOwner, issueError=True)
    return Action(Where, 0, 0, 0, Owner, NewOwner, Unit, 48, Count, 20)


def ModifyUnitHitPoints(Count, Unit, Owner, Where, Percent):
    """Set hit points for quantity units owned by player at location to percent%.

    This action will modify the specified unit(s) hit points. The hit points will be changed based on the percentage specified in the action trigger.
    """
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 49, Count, 20)


def ModifyUnitEnergy(Count, Unit, Owner, Where, Percent):
    """Set energy points for quantity units owned by player at location to percent%.

    This action will modify the specified unit(s) spell-casting energy. The energy will be changed based on the percentage specified in the action trigger.
    """
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 50, Count, 20)


def ModifyUnitShields(Count, Unit, Owner, Where, Percent):
    """Set shield points for quantity units owned by player at location to percent%.

    This action will modify the specified unit(s) shield points. The shield points will be changed based on the percentage specified in the action trigger.
    """
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Percent, Unit, 51, Count, 20)


def ModifyUnitResourceAmount(Count, Owner, Where, NewValue):
    """Set resource amount for quantity resource sources owned by player at location to quantity.

    This action allows you to modify the amount of resources contained in the various mineral stores. For example, you could modify a Vespene Geyser so that it had 0 resources if you desire.
    """
    Count = EncodeCount(Count, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, NewValue, 0, 52, Count, 4)


def ModifyUnitHangarCount(Add, Count, Unit, Owner, Where):
    """Add at most quantity to hangar for quantity units at location owned by player.

    This action will modify the contents of a unit(s) hangar. For example, this will allow you to add 5 additional Interceptors to the Carrier’s hangar.
    """
    Count = EncodeCount(Count, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    Owner = EncodePlayer(Owner, issueError=True)
    Where = EncodeLocation(Where, issueError=True)
    return Action(Where, 0, 0, 0, Owner, Add, Unit, 53, Count, 20)


def PauseTimer():
    """Pause the game.

    This action will put the game in a pause state. If a matching Unpause Game is not found, the program automatically unpauses the game when the current trigger is finished. Note that pause game has no effect in multiplayer scenarios or against computer controlled players.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 54, 0, 4)


def UnpauseTimer():
    """Unpause the countdown timer.

    This action will resume the timer from a paused session.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 55, 0, 4)


def Draw():
    """End the scenario in a draw for all players.

    This will end the scenario in a draw for the affected players. Any other players in the game will continue.
    """
    return Action(0, 0, 0, 0, 0, 0, 0, 56, 0, 4)


def SetAllianceStatus(Player, Status):
    """Set Player to Ally status.

    This allows you to set the value of the affected players’ alliance status.
    """
    Player = EncodePlayer(Player, issueError=True)
    Status = EncodeAllyStatus(Status, issueError=True)
    return Action(0, 0, 0, 0, Player, 0, Status, 57, 0, 4)


def SetMemory(dest, modtype, value):
    modtype = EncodeModifier(modtype, issueError=True)
    return Action(0, 0, 0, 0, EPD(dest), value, 0, 45, modtype, 20)


def SetMemoryEPD(dest, modtype, value):
    dest = EncodePlayer(dest, issueError=True)
    modtype = EncodeModifier(modtype, issueError=True)
    return Action(0, 0, 0, 0, dest, value, 0, 45, modtype, 20)


def SetNextPtr(trg, dest):
    return SetMemory(trg + 4, 7, dest)


def SetDeathsX(Player, Modifier, Number, Unit, Mask):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    return Action(Mask, 0, 0, 0, Player, Number, Unit, 45, Modifier, 20, eudx="SC")


def SetMemoryX(dest, modtype, value, mask):
    modtype = EncodeModifier(modtype, issueError=True)
    return SetDeathsX(EPD(dest), modtype, value, 0, mask)


def SetMemoryXEPD(epd, modtype, value, mask):
    modtype = EncodeModifier(modtype, issueError=True)
    return SetDeathsX(epd, modtype, value, 0, mask)


def SetKills(Player, Modifier, Number, Unit):
    Player = EncodePlayer(Player, issueError=True)
    Modifier = EncodeModifier(Modifier, issueError=True)
    Unit = EncodeUnit(Unit, issueError=True)
    if isinstance(Player, int) and Player >= 12:
        if Player == 13:
            return [
                SetMemory(0x6509B0, Add, -12 * 228),
                SetDeaths(CurrentPlayer, Modifier, Number, Unit),
                SetMemory(0x6509B0, Add, 12 * 228),
            ]
        ep_assert(
            Player <= 11, _("SetKills Player should be only P1~P12 or CurrentPlayer")
        )
    if isinstance(Unit, int):
        ep_assert(Unit <= 227, _("SetKills Unit should be at most 227"))
    return SetDeaths(Player - 228 * 12, Modifier, Number, Unit)
