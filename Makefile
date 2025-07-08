CC := gcc
CXX := g++
CXXFLAGS := -std=c++17 -pthread -Wall -Wextra -Werror
GTEST_DIR := /home/tools/googletest-1.14.0
BIN_DIR := bin
INCLUDES := -isystem $(GTEST_DIR)/googletest/include
LIBS := $(GTEST_DIR)/lib/libgtest.a $(GTEST_DIR)/lib/libgtest_main.a
SRC :=

.PHONY: all debug clean

all: prepare debug

prepare:
	ifeq ($(SRC),)
		$(error You need specify SRC, e.g. make SRC=/path/to/a.cpp)
	endif
	@mkdir -p $(BIN_DIR)

debug:
	$(CXX) $(SRC) $(CXXFLAGS) $(INCLUDES) $(LIBS) -o $(BIN_DIR)/run_tests

clean:
	rm -rf $(BIN_DIR)/