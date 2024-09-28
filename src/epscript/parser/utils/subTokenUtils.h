//
// Created by phu54321 on 2018-01-20.
//

#ifndef EPSCRIPT_SUBTOKENUTILS_H
#define EPSCRIPT_SUBTOKENUTILS_H

#include "../tokenizer/tokenizer.h"
#include <functional>

Token* subTokenListGetTail(Token* listRoot);
void subTokenListIter(const Token* listRoot, std::function<void(const Token*)> func);
size_t subTokenListLength(const Token* listRoot);

#endif //EPSCRIPT_SUBTOKENUTILS_H
