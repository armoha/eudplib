#include <vector>
#include <map>
#include <set>
#include "closure.h"
#include "eudplibGlobals.h"
#include "../parserUtilities.h"
#include <functional>

using std::string;

enum {
    TABLE_FUNC = 1,
    TABLE_VAR = 2,
    TABLE_CONST = 4,
    TABLE_MODULE = 8,
    TABLE_DECLONLY = 0x10
};

struct ClosureEntry {
    int type;
    string mappedString;
};

struct Closure {
    std::map<string, ClosureEntry> nameMap;
    std::set<string> mapValueSet;
};

class ClosureManagerImpl {
public:
    ClosureManagerImpl();
    ~ClosureManagerImpl();

    // Scoping
    void pushScope();
    void popScope();

    // Defining variables
    bool declareFunction(std::string& name);
    bool defFunction(std::string& name);
    bool defVariable(std::string& name);
    bool defConstant(std::string& name);
    bool defModule(std::string& name);

    // These function returns possibility. For example, Kills can be both
    // constant and function, so both function will return true to "Kills".
    bool getFunction(std::string& name) const;
    bool getConstant(std::string& name) const;
    bool getVariable(std::string& name) const;
    bool isModule(std::string& name) const;

private:
    Closure& lastClosure() { return closures[closures.size() - 1]; }
    bool hasOutputName(const std::string& name) const;
    const Closure* findNearestNameContainer(const std::string &name) const;
    bool defTableValue(std::string& name, int tableType);
    bool getTableValue(std::string& name, int tableType, std::function<bool(std::string&)> fallback) const;

private:
    std::vector<Closure> closures;
};


ClosureManager::ClosureManager() : impl(new ClosureManagerImpl) {}
ClosureManager::~ClosureManager() { delete impl; }

void ClosureManager::pushScope() { impl->pushScope(); }
void ClosureManager::popScope() { impl->popScope(); }

bool ClosureManager::declareFunction(std::string& name) { return impl->declareFunction(name); }
bool ClosureManager::defFunction(std::string& name) { return impl->defFunction(name); }
bool ClosureManager::defVariable(std::string& name) { return impl->defVariable(name); }
bool ClosureManager::defConstant(std::string& name) { return impl->defConstant(name); }
bool ClosureManager::defModule(std::string& name) { return impl->defModule(name); }

bool ClosureManager::getFunction(std::string& name) const { return impl->getFunction(name); }
bool ClosureManager::getConstant(std::string& name) const { return impl->getConstant(name); }
bool ClosureManager::getVariable(std::string& name) const { return impl->getVariable(name); }
bool ClosureManager::isModule(std::string &name) const { return impl->isModule(name); }

///////

ClosureManagerImpl::ClosureManagerImpl() {
    closures.push_back(Closure()); // Empty, default closure
}
ClosureManagerImpl::~ClosureManagerImpl() {}


bool ClosureManagerImpl::defFunction(std::string &name) {
    return defTableValue(name, TABLE_CONST | TABLE_FUNC);
}

bool ClosureManagerImpl::declareFunction(std::string &name){
    return defTableValue(name, TABLE_CONST | TABLE_FUNC | TABLE_DECLONLY);
}

bool ClosureManagerImpl::defVariable(std::string &name) {
    return defTableValue(name, TABLE_VAR);
}

bool ClosureManagerImpl::defConstant(std::string &name) {
    return defTableValue(name, TABLE_CONST);
}

bool ClosureManagerImpl::defModule(std::string &name) {
    return defTableValue(name, TABLE_MODULE | TABLE_CONST);
}

bool ClosureManagerImpl::getFunction(std::string& name) const {
    if (isBuiltinConst(name)) return true;
    return getTableValue(name, TABLE_FUNC | TABLE_CONST, [&](std::string& name1) {
        funcNamePreprocess(name1);
        if (isBuiltinConst(name)) return true;
        return getTableValue(name1, TABLE_FUNC | TABLE_CONST, [&](std::string& name2) {
            return false;
        });
    });
}

bool ClosureManagerImpl::getConstant(std::string& name) const {
    return getTableValue(name, TABLE_CONST, [&](std::string& name1) {
        return isBuiltinConst(name1);
    });
}

bool ClosureManagerImpl::getVariable(std::string& name) const {
    return getTableValue(name, TABLE_VAR, [](std::string&) { return false; });
}

bool ClosureManagerImpl::isModule(std::string& name) const {
    return getTableValue(name, TABLE_MODULE, [](std::string&) { return false; });
}

///////

const Closure* ClosureManagerImpl::findNearestNameContainer(const std::string &name) const {
    for(auto it = closures.rbegin() ; it != closures.rend() ; it++) {
        auto &map = it->nameMap;
        if (map.find(name) != map.end()) return &(*it);
    }
    return nullptr;
}

bool ClosureManagerImpl::getTableValue(std::string& name, int tableTypes, std::function<bool(std::string&)> fallback) const {
    auto closure = findNearestNameContainer(name);
    if (closure == nullptr) return fallback(name);
    const auto& cEntry = closure->nameMap.find(name)->second;
    if(cEntry.type & tableTypes) {
        name = cEntry.mappedString;
        return true;
    }
    else return false;
}

///////

void ClosureManagerImpl::pushScope() {
    closures.push_back(Closure());
}

void ClosureManagerImpl::popScope() {
    if(closures.size() == 1) throw std::logic_error("Cannot pop beyond default closure");
    closures.pop_back();
}

bool ClosureManagerImpl::defTableValue(std::string &name, int tableType) {
    auto& lastClosure = this->lastClosure();
    auto& map = lastClosure.nameMap;
    auto it = map.find(name);
    if(it != map.end()) { // Has duplicate name on this closure
        // If previously defined as declaration-only and declared type matches tableType,
        // just modify the declaration.
        if((it->second.type & TABLE_DECLONLY) && (it->second.type == (tableType | TABLE_DECLONLY))) {
            it->second.type = tableType;
            return true;
        }
        return false;
    }
    if(!hasOutputName(name)) {
        ClosureEntry entry = {tableType, name};
        map.insert(std::make_pair(name, entry));
        lastClosure.mapValueSet.insert(name);
        return true;
    }
    else {
        char postfix[30];
        int i;
        for(i = 1 ; ; i++) {
            sprintf(postfix, "_%d", i);
            std::string otherName = name + postfix;
            if(!hasOutputName(otherName)) {
                ClosureEntry entry = {tableType, otherName};
                map.insert(std::make_pair(name, entry));
                lastClosure.mapValueSet.insert(otherName);
                name = otherName;
                return true;
            }
        }
    }
}


bool ClosureManagerImpl::hasOutputName(const std::string& name) const {
    for(auto it = closures.rbegin() ; it != closures.rend() ; it++) {
        auto &set = it->mapValueSet;
        if (set.find(name) != set.end()) return true;
    }
    return false;
}
