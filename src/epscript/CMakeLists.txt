cmake_minimum_required(VERSION 3.6)
project(epScript)

set(EPSCRIPT_VERSION 1.3.1)
set(EPSCRIPT_SOVERSION 1.3)
set(EUDPLIB_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../eudplib/")
set(EUDDRAFT_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../euddraft/")

if (WIN32)
    set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} /MT")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /MT")
    # set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -s -static-libgcc -static")
    # set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -s -static-libgcc -static-libstdc++ -static")
    SET(CMAKE_AR  "gcc-ar")
    SET(CMAKE_C_ARCHIVE_CREATE "<CMAKE_AR> qcs <TARGET> <LINK_FLAGS> <OBJECTS>")
    SET(CMAKE_C_ARCHIVE_FINISH   true)
endif()

set_source_files_properties(parser/epparser.cpp PROPERTIES GENERATED TRUE)

if (WIN32)
    add_custom_command(
            OUTPUT ${CMAKE_SOURCE_DIR}/parser/epparser.cpp ${CMAKE_SOURCE_DIR}/parser/epparser.h
            DEPENDS ./lemon2.exe parser/epparser.lemon
            COMMAND ./lemon2 -p -c -l parser/epparser.lemon
            COMMAND cmake -E copy parser/epparser.c parser/epparser.cpp
            COMMAND cmake -E remove parser/epparser.c
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            VERBATIM
    )

else ()
    add_custom_command(
            OUTPUT ${CMAKE_SOURCE_DIR}/parser/epparser.cpp ${CMAKE_SOURCE_DIR}/parser/epparser.h
            DEPENDS ./lemon2 parser/epparser.lemon
            COMMAND ./lemon2 -p -c -l parser/epparser.lemon
            COMMAND cmake -E rm -f parser/epparser.cpp
            COMMAND cmake -E rename parser/epparser.c parser/epparser.cpp
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            VERBATIM
    )

endif()

set(CMAKE_CXX_STANDARD 11)
set(SOURCE_FILES ${CMAKE_SOURCE_DIR}/parser/epparser.cpp parser/tokenizer/tokenizer.cpp
        parser/tokenizer/tokChars.cpp parser/tokenizer/tokenizerImpl.cpp
        parser/generator/pygen.cpp parser/tokenAdapter.cpp
        parser/reservedWords/condact.cpp parser/generator/eudplibGlobals.cpp parser/generator/closure.cpp
        parser/generator/closure.h parser/parser.h parser/parserUtils.cpp parser/parserUtilsTokens.cpp utils.cpp
        parser/reservedWords/constparser.cpp parser/reservedWords/constparser.h parser/utils/subTokenUtils.cpp parser/utils/subTokenUtils.h parser/utils/traceUtils.cpp parser/tokenizer/token.cpp parser/tokenizer/token.h)

set(TEST_SOURCE_FILES
        test/test_tokenizer.cpp test/test_pygen.cpp test/test_base.cpp test/parser/test_arraydecl.cpp
        test/parser/test_complex.cpp test/parser/test_ctrlstru.cpp
        test/parser/test_globalv.cpp test/parser/test_import.cpp
        test/parser/test_object.cpp test/parser/test_ternary.cpp test/parser/test_pyliteral.cpp
        test/parser/test_expression.cpp test/test_testtool.cpp test/parser/test_function.cpp test/parser/test_lambda.cpp test/parser/test_debuginfo.cpp test/parser/test_staticv.cpp test/parser/test_bugcase_4.cpp test/parser/test_arrw_inc.cpp)

add_definitions(-DVERSION="${EPSCRIPT_VERSION}")

# Shared library (.dll/.so)
add_library(epScriptLib SHARED ${SOURCE_FILES} libmain.cpp)
set_target_properties(epScriptLib  PROPERTIES
        VERSION ${EPSCRIPT_VERSION}
        SOVERSION ${EPSCRIPT_SOVERSION}
        )

# Python binding (.pyd/.so)
add_subdirectory(pybind11)
pybind11_add_module(pyepScript ${SOURCE_FILES} pybindmain.cpp)

# Testing
add_executable(epScriptTest ${SOURCE_FILES} ${TEST_SOURCE_FILES} test/testmain.cpp)
set_target_properties(epScriptTest PROPERTIES
        COMPILE_DEFINITIONS MEMORY_DEBUG)

add_executable(epScriptProfile ${SOURCE_FILES} libmain.cpp test/stresstest.cpp)


if (CMAKE_BUILD_TYPE MATCHES "Release")
    message("release mode - static linked")
    add_custom_command(TARGET epScriptLib POST_BUILD
            # COMMAND "${CMAKE_COMMAND}" -E copy "$<TARGET_LINKER_FILE:epScriptLib>" "${EUDPLIB_PATH}epscript/$<TARGET_LINKER_FILE_NAME:libepScriptLib>"
            # COMMAND "${CMAKE_COMMAND}" -E copy "$<TARGET_LINKER_FILE:epScriptLib>" "${EUDDRAFT_PATH}$<TARGET_LINKER_FILE_NAME:libepScriptLib>"
            COMMENT "Copying to other projects - eudtrglib & euddraft"
            VERBATIM)
    add_custom_command(TARGET pyepScript POST_BUILD
            COMMAND "${CMAKE_COMMAND}" -E copy "$<TARGET_LINKER_FILE:pyepScript>" "${CMAKE_CURRENT_SOURCE_DIR}/../eudplib/epscript/$<TARGET_LINKER_FILE_NAME:pyepScript>"
            COMMENT "Copying python extension to pyepScript"
            VERBATIM)
endif()
