//
// Created by phu54321 on 2017-01-09.
//

#include "utils.h"
#include "parser/parser.h"
#include <stdexcept>
#include <string.h>
#include <vector>
#include <unordered_set>

extern std::unordered_set<std::string> builtinConstSet;

extern bool MAP_DEBUG;

extern "C"
{
    void EPS_EXPORT setDebugMode(int set)
    {
        MAP_DEBUG = set != 0;
    }

    void EPS_EXPORT registerPlibConstants(const char *zeroSeparatedStrings)
    {
        const char *p = zeroSeparatedStrings;
        std::vector<std::string> vector;

        do
        {
            std::string globalName(p);
            builtinConstSet.insert(globalName);
            p += globalName.size() + 1;
        } while (*p);
    }

    int EPS_EXPORT getErrorCount()
    {
        return getParseErrorNum();
    }

    EPS_EXPORT const char *compileString(
        const char *filename,
        const char *rawcode)
    {
        // Remove \r from code
        std::vector<char> cleanCode;
        cleanCode.reserve(strlen(rawcode) + 1);
        const char *p = rawcode;
        while (*p)
        {
            if (*p != '\r')
                cleanCode.push_back(*p);
            p++;
        }
        std::string code(cleanCode.begin(), cleanCode.end());

        try
        {
            auto parsed = ParseString(filename, code);
            parsed = addStubCode(parsed);
            char *s = new char[parsed.size() + 1];
            memcpy(s, parsed.data(), parsed.size());
            s[parsed.size()] = '\0';
            return s;
        }
        catch (std::runtime_error e)
        {
            fprintf(stderr, "Error occurred : %s\n", e.what());
            return nullptr;
        }
    }

    void EPS_EXPORT freeCompiledResult(const char *str)
    {
        delete[] str;
    }
}
