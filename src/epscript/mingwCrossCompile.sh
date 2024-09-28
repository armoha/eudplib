#!/bin/sh
mkdir -p cmake-release-mingw
cd cmake-release-mingw
cmake -D CMAKE_TOOLCHAIN_FILE=../Mingw32-Crosscompile.cmake -DCMAKE_BUILD_TYPE=Release ..
make -j4
cd ..
