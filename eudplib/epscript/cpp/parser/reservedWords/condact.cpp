#include "condAct.h"

const char* conditionList[] = {
    "CountdownTimer", "Command", "Bring", "Accumulate", "Kills",
    "CommandMost", "CommandMostAt", "MostKills", "HighestScore", "MostResources",
    "Switch", "ElapsedTime", "Opponents", "Deaths", "CommandLeast",
    "CommandLeastAt", "LeastKills", "LowestScore", "LeastResources", "Score",
    "Always", "Never", "Memory", "MemoryEPD",
    "DeathsX", "MemoryX", "MemoryXEPD",
};

const char* actionList[] = {
    "Victory", "Defeat", "PreserveTrigger", "Wait", "PauseGame", "UnpauseGame",
    "Transmission", "PlayWAV", "DisplayText", "CenterView",
    "CreateUnitWithProperties", "SetMissionObjectives", "SetSwitch",
    "SetCountdownTimer", "RunAIScript", "RunAIScriptAt", "LeaderBoardControl",
    "LeaderBoardControlAt", "LeaderBoardResources", "LeaderBoardKills",
    "LeaderBoardScore", "KillUnit", "KillUnitAt", "RemoveUnit", "RemoveUnitAt",
    "SetResources", "SetScore", "MinimapPing", "TalkingPortrait", "MuteUnitSpeech",
    "UnMuteUnitSpeech", "LeaderBoardComputerPlayers", "LeaderBoardGoalControl",
    "LeaderBoardGoalControlAt", "LeaderBoardGoalResources", "LeaderBoardGoalKills",
    "LeaderBoardGoalScore", "MoveLocation", "MoveUnit", "LeaderBoardGreed",
    "SetNextScenario", "SetDoodadState", "SetInvincibility", "CreateUnit",
    "SetDeaths", "Order", "Comment", "GiveUnits", "ModifyUnitHitPoints",
    "ModifyUnitEnergy", "ModifyUnitShields", "ModifyUnitResourceAmount",
    "ModifyUnitHangarCount", "PauseTimer", "UnpauseTimer", "Draw",
    "SetAllianceStatus", "SetMemory", "SetNextPtr", "SetMemoryEPD", "SetCurrentPlayer",
    "SetDeathsX", "SetMemoryX", "SetMemoryXEPD", "SetKills",
};

const char* actionAllpList[] = {
    "PlayWAVAll", "DisplayTextAll", "CenterViewAll", "SetMissionObjectivesAll",
    "MinimapPingAll", "TalkingPortraitAll",
};

bool isConditionName(const std::string& name) {
    for(const char* cname : conditionList) {
        if(name == cname) return true;
    }
    return false;
}

bool isActionName(const std::string& name) {
    for(const char* aname : actionList) {
        if(name == aname) return true;
    }
    return false;
}

bool isActionAllpName(const std::string& name) {
    for(const char* aname : actionAllpList) {
        if(name == aname) return true;
    }
    return false;
}
