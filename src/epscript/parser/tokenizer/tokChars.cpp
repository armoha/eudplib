#include <cstdio>
#include "tokChars.h"

bool isNameLeadChar(char ch) {
    return (
            ch == '_' || ch == '$' ||
            (ch != EOF && ch < 0) ||
            ('a' <= ch && ch <= 'z') ||
            ('A' <= ch && ch <= 'Z')
    );
}

bool isNameBodyChar(char ch) {
    return (
            ch == '_' ||
            (ch != EOF && ch < 0) ||
            ('a' <= ch && ch <= 'z') ||
            ('A' <= ch && ch <= 'Z') ||
            ('0' <= ch && ch <= '9')
    );
}

bool isSpaceOrNewline(char ch) {
    return ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n';
}


int getXDigitInt(char ch) {
    if('0' <= ch && ch <= '9') return ch - '0';
    else if('a' <= ch && ch <= 'f') return ch - 'a' + 10;
    else if('A' <= ch && ch <= 'F') return ch - 'A' + 10;
    else return -1;
}