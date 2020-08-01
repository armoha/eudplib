//
// Created by 박현우 on 2016. 11. 30..
//

#ifndef EPSCRIPT_UTILS_H_H
#define EPSCRIPT_UTILS_H_H

#include <string>
std::string getFile(const std::string &fname);

#if defined(_WIN32)
#if defined(epScriptLib_EXPORTS)
#define EPS_EXPORT __declspec(dllexport)
#else
#define EPS_EXPORT
#endif
#else
#define EPS_EXPORT
#endif

#endif //EPSCRIPT_UTILS_H_H
