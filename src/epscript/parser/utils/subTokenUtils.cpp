//
// Created by phu54321 on 2018-01-20.
//

#include "subTokenUtils.h"

Token* subTokenListGetTail(Token* listRoot) {
    while(1) {
        if (listRoot->subToken[1]) {
            listRoot = listRoot->subToken[1];
        }
        else return listRoot;
    }
}

void subTokenListIter(const Token* listRoot, std::function<void(const Token*)> func) {
    while (listRoot) {
        func(listRoot->subToken[0]);
        listRoot = listRoot->subToken[1];
    }
}

size_t subTokenListLength(const Token* listRoot) {
    int length = 0;
    while(listRoot) {
        length++;
        listRoot = listRoot->subToken[1];
    }
    return length;
}
