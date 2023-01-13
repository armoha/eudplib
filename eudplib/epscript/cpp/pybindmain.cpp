//
// Created by phu54321 on 2017-01-09.
//

#include "utils.h"
#include "parser/parser.h"
#include <stdexcept>
#include <string.h>
#include <vector>
#include <unordered_set>
#include <pybind11/pybind11.h>

extern std::unordered_set<std::string> builtinConstSet;
extern std::unordered_set<std::string> pyKeywordSet;
extern std::unordered_set<std::string> pyBuiltinSet;

extern bool MAP_DEBUG;

void EPS_EXPORT setDebugMode(int set) {
    MAP_DEBUG = set != 0;
}

void EPS_EXPORT registerPlibConstants(const char* zeroSeparatedStrings) {
    const char* p = zeroSeparatedStrings;
    std::vector<std::string> vector;

    do {
        std::string globalName(p);
        builtinConstSet.insert(globalName);
        p += globalName.size() + 1;
    } while ( *p);
}

void EPS_EXPORT registerPyKeywords(const char *zeroSeparatedStrings) {
    const char *p = zeroSeparatedStrings;
    std::vector<std::string> vector;

    do {
        std::string keywordName(p);
        pyKeywordSet.insert(keywordName);
        p += keywordName.size() + 1;
    } while (*p);
}

void EPS_EXPORT registerPyBuiltins(const char *zeroSeparatedStrings) {
    const char *p = zeroSeparatedStrings;
    std::vector<std::string> vector;

    do {
        std::string builtinName(p);
        pyBuiltinSet.insert(builtinName);
        p += builtinName.size() + 1;
    } while (*p);
}

int EPS_EXPORT getErrorCount() {
    return getParseErrorNum();
}

const char *EPS_EXPORT compileString(
        const char *filename,
        const char *rawcode
) {
    // Remove \r from code
    std::vector<char> cleanCode;
    cleanCode.reserve(strlen(rawcode) + 1);
    const char* p = rawcode;
    while(*p) {
        if(*p != '\r') cleanCode.push_back(*p);
        p++;
    }
    std::string code(cleanCode.begin(), cleanCode.end());

    try {
        auto parsed = ParseString(filename, code);
        parsed = addStubCode(parsed);
        char *s = new char[parsed.size() + 1];
        memcpy(s, parsed.data(), parsed.size());
        s[parsed.size()] = '\0';
        return s;
    } catch (std::runtime_error e) {
        fprintf(stderr, "Error occurred : %s\n", e.what());
        return nullptr;
    }
}

void EPS_EXPORT freeCompiledResult(const char *str) {
    delete[] str;
}

PYBIND11_MODULE(epScript, m) {
    m.def("setDebugMode", &setDebugMode, "Set debug mode.");
    m.def("registerPlibConstants", &registerPlibConstants, "Register eudplib constants");
    m.def("getErrorCount", &getErrorCount, "Get compile error count");
    m.def("compileString", &compileString, "Compile string");
    m.def("freeCompiledResult", &freeCompiledResult, "Free compiled string");
}


