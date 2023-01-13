//
// Created by phu54321 on 2016-11-29.
//

#ifndef EPSCRIPT_CLOSURE_H
#define EPSCRIPT_CLOSURE_H

#include <string>

class ClosureManagerImpl;

class ClosureManager {
public:
    ClosureManager();
    ~ClosureManager();

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
    // These functions will also change given name's value to match it to closure's name
    bool getFunction(std::string& name) const;
    bool getConstant(std::string& name) const;
    bool getVariable(std::string& name) const;
    bool isModule(std::string& name) const;

private:
    ClosureManagerImpl* impl;
};

#endif //EPSCRIPT_CLOSURE_H
