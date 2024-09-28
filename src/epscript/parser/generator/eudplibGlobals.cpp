#include <unordered_set>
#include "eudplibGlobals.h"
#include <iostream>

std::unordered_set<std::string> builtinConstSet = {
        "onPluginStart", "beforeTriggerExec", "afterTriggerExec",
        "f_dwread", "SetTo", "EUDArray", "EUDByteReader", "f_dwread_epd"
};
std::unordered_set<std::string> pyKeywordSet = {"is", "for", "from", "if"};
std::unordered_set<std::string> pyBuiltinSet = {"print", "str", "tuple", "type", "vars"};

bool isBuiltinConst(std::string& name) {
    if(name == "True" || name == "true") {
        name = "True";
        return true;
    }

    else if(name == "False" || name == "false") {
        name = "False";
        return true;
    }
    else if (name == "None") return true;

    else {
        return builtinConstSet.find(name) != builtinConstSet.end();
    }
}

bool isPyKeyword(std::string& name) {
    return pyKeywordSet.find(name) != pyKeywordSet.end();
}

bool isPyBuiltin(std::string& name) {
    return pyBuiltinSet.find(name) != pyBuiltinSet.end();
}
