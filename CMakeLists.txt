cmake_minimum_required(VERSION 3.4)
project(PokerFastutils)

set(CMAKE_VERBOSE_MAKEFILE ON)

if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE "Release")
endif()

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
  add_compile_definitions(DEBUG)
  add_compile_options(-g)
  add_compile_options(-O0)
  message(STATUS "Running debug build")
else()
  add_compile_definitions(NDEBUG)
  add_compile_options(-g)
  add_compile_options(-O3)
  message(STATUS "Running release build")
endif()

add_subdirectory("extern/pybind11")
pybind11_add_module(PokerFastutils src/poker_fastutils.cpp)
