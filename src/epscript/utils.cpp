#include "utils.h"
#include <stdio.h>
#include <vector>
#include <stdexcept>

std::string getFile(const std::string& fname) {
    FILE* fp = fopen(fname.c_str(), "rb");
    if(fp == nullptr) {
        throw std::runtime_error("Input file not found : " + fname);
    }

    fseek(fp, 0, SEEK_END);
    size_t fsize = static_cast<size_t>(ftell(fp));
    rewind(fp);

    std::vector<char> fdata;
    fdata.reserve(fsize);
    while(1) {
        char ch = static_cast<char>(fgetc(fp));
        if(feof(fp)) break;
        if(ch == '\r') continue;
        fdata.push_back(ch);
    }

    fclose(fp);
    return std::string(fdata.begin(), fdata.end());
}

