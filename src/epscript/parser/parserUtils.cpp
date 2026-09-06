#include <string>
#include <stdexcept>
#include <vector>
#include <regex>
#include <iostream>
#include <sstream>
#include <cstring>

#include "generator/pygen.h"
#include "generator/eudplibGlobals.h"
#include "parserUtilities.h"
#include "reservedWords/constparser.h"
#include "reservedWords/condAct.h"

extern int currentTokenizingLine;
extern std::string currentModule;

int errorn = 0;

void throw_error(int code, const std::string& message, int line) {
    if (line == -1) line = currentTokenizingLine;
    if (errorn < 100) {
        std::cerr << "[Error " << code << "] Module \"" << currentModule << "\" Line " << line << " : " << message << std::endl;
        (*pGen) << "# [Error " << code << "] Line " << line << " : " << message << std::endl;
        if (++errorn == 100) {
            std::cerr << " - More than 100 errors occurred. Stop printing errors" << std::endl;
        }
    }
}

int resetParserErrorNum() {
    errorn = 0;
    return 0;
}

int getParseErrorNum() {
    return errorn;
}


////

void writeCsOpener(std::ostream& os, const Token* csOpener, const Token* lexpr) {
    os << "if " << csOpener->data;
    applyNegativeOptimization(os, lexpr);
    os << ":" << std::endl;
}

void applyNegativeOptimization(std::ostream& os, const Token *lexpr) {
    if(lexpr->type == TOKEN_LNOT) {
        os << "(" << lexpr->subToken[0]->data << ", neg=True)";
    }
    else if(lexpr->type == TOKEN_NE) {
        os << "(" << lexpr->subToken[0]->data << " == " << lexpr->subToken[1]->data << ", neg=True)";
    }
    else {
        os << "(" << lexpr->data << ")";
    }
}



void commaListIter(std::string& s, std::function<void(std::string&)> func) {
    if (s.empty()) return;

    bool isFirst = true;
    std::string out;
    const char *p = s.c_str(), *p2 = p;
    while(1) {
        while(*p2 != '\0' && *p2 != ',') p2++;
        std::string value(p, p2 - p);
        func(value);
        if(isFirst) isFirst = false;
        else out += ", ";
        out += value;
        if(*p2 == '\0') break;
        p2++;
        while(*p2 == ' ') p2++;
        p = p2;
    }
    s = out;
}

void writeStringList(std::ostream& os, const std::vector<std::string>& slist) {
    if(!slist.empty()) {
        os << slist[0];
        for(size_t i = 1 ; i < slist.size() ; i++) {
            os << ", " << slist[i];
        }
    }
}

void funcNamePreprocess(std::string& s) {
    if(strncmp(s.c_str(), "py_", 3) == 0) return; // Builtin function?
    else if(isBuiltinConst(s)) return;  // Some builtin function don't have f_ prefixes. (b2i4) Pass them as-is
    else if('a' <= s[0] && s[0] <= 'z') {  // Name starts with lowercase -> Prepend "f_"
        s = "f_" + s;
        return;
    }
    else return;
}

bool impPathProcess(const std::string& s, std::string& impPath, std::string& impModname) {
    // Preprocess python module.
    auto lastDot = s.find_last_of('.');
    std::string path, modname;
    bool isPy;
    if(lastDot == std::string::npos) {
        modname = s;
    }
    else {
        path = s.substr(0, lastDot);
        modname = s.substr(lastDot + 1);
        if (path.find_first_not_of('.') == std::string::npos) path += '.';
    }
    if(strncmp(modname.c_str(), "py_", 3) == 0) {
        impPath = path;
        impModname = modname.substr(3);
        isPy = true;
    }
    else {
        impPath = path;
        impModname = modname;
        isPy = false;
    }
    return isPy;
}

////


std::string trim(std::string s) {
    // ltrim
    size_t startpos = s.find_first_not_of(" \n\t");
    if (std::string::npos != startpos)
    {
        s = s.substr(startpos);
    }

    // rtrim
    size_t endpos = s.find_last_not_of(" \n\t");
    if (std::string::npos != endpos)
    {
        s = s.substr(0, endpos + 1);
    }
    return s;
}


static std::regex iwCollapseRegex("\n( *)(_t\\d+) = (EUDWhile|EUDIf|EUDElseIf)\\(\\)\n\\1if \\2\\((.+)\\):");
std::string iwCollapse(const std::string& in) {
    return std::regex_replace(in, iwCollapseRegex, "\n$1if $3()($4):");
}

static std::string extractDoActionsInner(const std::string& trimmed) {
    if (trimmed.size() <= 10 || trimmed.substr(0, 10) != "DoActions(") {
        return "";
    }
    int depth = 1;
    size_t start = 10;
    size_t end = std::string::npos;
    for (size_t i = start; i < trimmed.size(); i++) {
        if (trimmed[i] == '(') depth++;
        else if (trimmed[i] == ')') {
            depth--;
            if (depth == 0) { end = i; break; }
        }
    }
    if (end == std::string::npos || end <= start) return "";
    return trimmed.substr(start, end - start);
}

static bool isSafeIdentifier(const std::string& s) {
    if (constMap.find(s) != constMap.end()) return true;
    if (s == "True" || s == "False" || s == "None") return true;
    return false;
}

static bool isActionArgSafe(const std::string& arg) {
    std::string s = trim(arg);
    if (s.empty()) return false;

    if (s[0] == '\'' || s[0] == '"') return true;

    if (s[0] == '-' || s[0] == '+' || s[0] == '~') s = s.substr(1);
    if (s.empty()) return false;

    if (s.size() >= 2 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) {
        bool validHex = true;
        for (size_t i = 2; i < s.size(); i++) {
            char c = s[i];
            if (!std::isxdigit(static_cast<unsigned char>(c))) { validHex = false; break; }
        }
        if (validHex && s.size() > 2) return true;
    }

    if (s.size() >= 2 && s[0] == '0' && (s[1] == 'b' || s[1] == 'B')) {
        bool validBin = true;
        for (size_t i = 2; i < s.size(); i++) {
            char c = s[i];
            if (c != '0' && c != '1') { validBin = false; break; }
        }
        if (validBin && s.size() > 2) return true;
    }

    bool allDigits = true;
    for (char c : s) {
        if (!std::isdigit(static_cast<unsigned char>(c))) {
            allDigits = false;
            break;
        }
    }
    if (allDigits && !s.empty()) return true;

    if (isSafeIdentifier(s)) return true;

    return false;
}

static bool isDoActionsSafe(const std::string& inner) {
    size_t paren = inner.find('(');
    if (paren == std::string::npos || paren == 0) return false;

    std::string actionName = trim(inner.substr(0, paren));
    if (!isActionName(actionName) && !isActionAllpName(actionName)) return false;

    size_t rparen = inner.rfind(')');
    if (rparen == std::string::npos || rparen <= paren) return false;

    std::string args = inner.substr(paren + 1, rparen - paren - 1);

    int depth = 0;
    std::string current;
    for (size_t i = 0; i < args.size(); i++) {
        char c = args[i];
        if (c == '(') { depth++; current += c; }
        else if (c == ')') {
            if (depth == 0) return false;
            depth--;
            current += c;
        }
        else if (c == ',' && depth == 0) {
            if (!isActionArgSafe(current)) return false;
            current.clear();
        } else {
            current += c;
        }
    }
    if (!current.empty()) {
        if (!isActionArgSafe(current)) return false;
    }
    return true;
}

std::string mergeDoActions(const std::string& in) {
    std::istringstream iss(in);
    std::string line;
    std::vector<std::string> pending;
    std::vector<std::vector<std::string>> pendingComments;
    std::vector<std::string> commentBuffer;
    std::string pendingIndent;
    std::ostringstream out;
    auto flush = [&]() {
        if (pending.empty()) {
            return;
        }
        if (pending.size() <= 1) {
            for (auto& c : pendingComments[0]) out << c;
            out << pendingIndent << "DoActions(" << pending[0] << ")\n";
            pending.clear();
            pendingComments.clear();
            return;
        }
        std::string actionIndent = pendingIndent + "    ";
        out << pendingIndent << "DoActions(\n";
        for (size_t i = 0; i < pending.size(); i++) {
            for (auto& c : pendingComments[i]) {
                std::string t = trim(c);
                out << actionIndent << t << "\n";
            }
            out << actionIndent << pending[i] << ",\n";
        }
        out << pendingIndent << ")\n";
        pending.clear();
        pendingComments.clear();
    };
    while (std::getline(iss, line)) {
        std::string trimmed = trim(line);
        if (!trimmed.empty() && trimmed[0] == '#') {
            commentBuffer.push_back(line + "\n");
            continue;
        }
        std::string inner = extractDoActionsInner(trimmed);
        if (!inner.empty() && isDoActionsSafe(inner)) {
            size_t first = line.find_first_not_of(" \t");
            std::string indent = (first != std::string::npos) ? line.substr(0, first) : "";
            if (!pending.empty() && indent == pendingIndent) {
                pending.push_back(inner);
            } else {
                flush();
                pending.push_back(inner);
                pendingIndent = indent;
            }
            std::vector<std::string> oneComment;
            if (!commentBuffer.empty()) {
                oneComment.push_back(std::move(commentBuffer.front()));
                commentBuffer.erase(commentBuffer.begin());
            }
            pendingComments.push_back(std::move(oneComment));
        } else {
            flush();
            for (auto& c : commentBuffer) out << c;
            commentBuffer.clear();
            out << line << "\n";
        }
    }
    flush();
    for (auto& c : commentBuffer) out << c;
    commentBuffer.clear();
    return out.str();
}

const char* stubCode =
    "## NOTE: THIS FILE IS GENERATED BY EPSCRIPT! DO NOT MODITY\n"
    "from eudplib import *\n"
    "from eudplib.core.eudfunc import EUDTraceLog, EUDTracedFunc, EUDTracedTypedFunc, EUDTracedMethod, EUDTracedTypedMethod\n"
    "from eudplib.epscript.helper import _RELIMP, _TYGV, _TYSV, _TYLV, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LSH, _ALL\n";

std::string addStubCode(const std::string& s) {
    return stubCode + s;
}

bool checkPyBuiltinForEpsGlobalConst(std::string& name) {
    if(strncmp(currentModule.c_str(), "BGM", 3) == 0 && name == "str") return false;
    return isPyBuiltin(name);
}
