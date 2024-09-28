//
// Created by phu54321 on 2016-12-01.
//

#include "constparser.h"
#include <map>

std::map<std::string, int> constMap;

void initConstmap() {

    //  AllyStatusDict
    constMap.insert(std::make_pair("Enemy", 0));
    constMap.insert(std::make_pair("Ally", 1));
    constMap.insert(std::make_pair("AlliedVictory", 2));

    //  ComparisonDict
    constMap.insert(std::make_pair("AtLeast", 0));
    constMap.insert(std::make_pair("AtMost", 1));
    constMap.insert(std::make_pair("Exactly", 10));

    //  ModifierDict
    constMap.insert(std::make_pair("SetTo", 7));
    constMap.insert(std::make_pair("Add", 8));
    constMap.insert(std::make_pair("Subtract", 9));

    //  OrderDict
    constMap.insert(std::make_pair("Move", 0));
    constMap.insert(std::make_pair("Patrol", 1));
    constMap.insert(std::make_pair("Attack", 2));

    //  PlayerDict
    constMap.insert(std::make_pair("P1", 0));
    constMap.insert(std::make_pair("P2", 1));
    constMap.insert(std::make_pair("P3", 2));
    constMap.insert(std::make_pair("P4", 3));
    constMap.insert(std::make_pair("P5", 4));
    constMap.insert(std::make_pair("P6", 5));
    constMap.insert(std::make_pair("P7", 6));
    constMap.insert(std::make_pair("P8", 7));
    constMap.insert(std::make_pair("P9", 8));
    constMap.insert(std::make_pair("P10", 9));
    constMap.insert(std::make_pair("P11", 10));
    constMap.insert(std::make_pair("P12", 11));
    constMap.insert(std::make_pair("Player1", 0));
    constMap.insert(std::make_pair("Player2", 1));
    constMap.insert(std::make_pair("Player3", 2));
    constMap.insert(std::make_pair("Player4", 3));
    constMap.insert(std::make_pair("Player5", 4));
    constMap.insert(std::make_pair("Player6", 5));
    constMap.insert(std::make_pair("Player7", 6));
    constMap.insert(std::make_pair("Player8", 7));
    constMap.insert(std::make_pair("Player9", 8));
    constMap.insert(std::make_pair("Player10", 9));
    constMap.insert(std::make_pair("Player11", 10));
    constMap.insert(std::make_pair("Player12", 11));
    constMap.insert(std::make_pair("CurrentPlayer", 13));
    constMap.insert(std::make_pair("Foes", 14));
    constMap.insert(std::make_pair("Allies", 15));
    constMap.insert(std::make_pair("NeutralPlayers", 16));
    constMap.insert(std::make_pair("AllPlayers", 17));
    constMap.insert(std::make_pair("Force1", 18));
    constMap.insert(std::make_pair("Force2", 19));
    constMap.insert(std::make_pair("Force3", 20));
    constMap.insert(std::make_pair("Force4", 21));
    constMap.insert(std::make_pair("NonAlliedVictoryPlayers", 26));

    //  PropStateDict
    constMap.insert(std::make_pair("Enable", 4));
    constMap.insert(std::make_pair("Disable", 5));
    constMap.insert(std::make_pair("Toggle", 6));

    //  ResourceDict
    constMap.insert(std::make_pair("Ore", 0));
    constMap.insert(std::make_pair("Gas", 1));
    constMap.insert(std::make_pair("OreAndGas", 2));

    //  ScoreDict
    constMap.insert(std::make_pair("Total", 0));
    constMap.insert(std::make_pair("Units", 1));
    constMap.insert(std::make_pair("Buildings", 2));
    constMap.insert(std::make_pair("UnitsAndBuildings", 3));
    // {"Kills", 4},   - word Kills are specially processed
    constMap.insert(std::make_pair("Razings", 5));
    constMap.insert(std::make_pair("KillsAndRazings", 6));
    constMap.insert(std::make_pair("Custom", 7));

    //  SwitchActionDict
    constMap.insert(std::make_pair("Set", 4));
    constMap.insert(std::make_pair("Clear", 5));
    constMap.insert(std::make_pair("Toggle", 6));
    constMap.insert(std::make_pair("Random", 11));

    //  SwitchStateDict
    constMap.insert(std::make_pair("Set", 2));
    constMap.insert(std::make_pair("Cleared", 3));
}

int parseConstantName(const std::string& name) {
    static bool constMapInitialized = false;
    if(!constMapInitialized) {
        constMapInitialized = true;
        initConstmap();
    }

    if(name.size() == 0 || name[0] != '$') return -1;
    auto it = constMap.find(name.substr(1));
    if (it == constMap.end()) return -1;
    else return it->second;
}
