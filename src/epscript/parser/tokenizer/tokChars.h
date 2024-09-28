//
// Created by 박현우 on 2016. 11. 27..
//

#ifndef EPSCRIPT_TOKCHARS_H
#define EPSCRIPT_TOKCHARS_H

bool isNameLeadChar(char ch);
bool isNameBodyChar(char ch);
bool isSpaceOrNewline(char ch);
int getXDigitInt(char ch);

#endif //EPSCRIPT_TOKCHARS_H
