#ifndef EPSCRIPT_EUDPLIBGLOBALS_H
#define EPSCRIPT_EUDPLIBGLOBALS_H

#include <string>
bool isBuiltinConst(std::string& name);
bool isPyKeyword(std::string& name);
bool isPyBuiltin(std::string& name);

#endif //EPSCRIPT_EUDPLIBGLOBALS_H
