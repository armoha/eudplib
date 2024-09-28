#!/bin/sh
mkdir -p cmake-release-wine
cd cmake-release-wine
WINEDEBUG=-all wine cmake -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release ..
WINEDEBUG=-all wine make -j4
cd ..
