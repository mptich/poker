cmake_minimum_required(VERSION 3.4)
project(PokerFastutils)

add_subdirectory("extern/pybind11")
pybind11_add_module(PokerFastutils src/poker_fastutils.cpp)
