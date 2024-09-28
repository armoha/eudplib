#ifndef EPSCRIPT_PRASER_H
#define EPSCRIPT_PRASER_H

#include <string>
std::string ParseString(const std::string& modname, const std::string& code, bool addComment=true);
std::string addStubCode(const std::string& _s);
int getParseErrorNum();

#endif //EPSCRIPT_PRASER_H
