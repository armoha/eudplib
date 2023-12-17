eudplib : EUD python library
============================
``eudplib`` is a StarCraft Use Map Setting(UMS) map tool library for Python programming language.

Fork of https://github.com/phu54321/eudplib

For easy-to-use executable, see https://github.com/armoha/euddraft/releases

Features
--------
* Support opening (unprotected) map and extracting scenario.chk data
* Powerful trigger scripting
* Edit input map to compile output EUD map
* ``epScript``, scripting language for StarCraft Trigger similar to JavaScript

Where is the issue tracker?
---------------------------

The eudplib issue tracker lives in `euddraft repository <https://github.com/armoha/euddraft/issues/>`_.

Since euddraft is standalone distribution for Python, eudplib, freeze map protector and epTrace line profiler, it's convenient to use a single issue tracker for both.

How to build ``libepScript.dll``
--------------------------------
Windows
^^^^^^^
Requires CMake, MSVC, Python >= 3.10

#. ``git clone https://github.com/armoha/eudplib --recursive``
#. ``cd eudplib/eudplib/epscript/cpp``
#. ``mkdir build``
#. ``cd build``
#. ``cmake .. -A x64 -DCMAKE_BUILD_TYPE=Release``
#. ``msbuild ALL_BUILD.vcxproj /p:Configuration=Release /p:Platform=x64``
