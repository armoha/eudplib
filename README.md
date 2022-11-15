# eudplib : EUD python library

Python library for making `Use Map Setting(UMS)` maps in **StarCraft: Remastered**.

Fork of https://github.com/phu54321/eudplib

For easy-to-use executable, see https://github.com/armoha/euddraft/releases

## How to build `libepScript.dll`
### Windows
Requires CMake, MSVC, Python >= 3.10
1. `git clone https://github.com/armoha/eudplib --recursive`
2. `cd eudplib/eudplib/epscript/cpp`
3. `mkdir build`
4. `cd build`
5. `cmake .. -A x64 -DCMAKE_BUILD_TYPE=Release`
6. `msbuild ALL_BUILD.vcxproj /p:Configuration=Release /p:Platform=x64`
