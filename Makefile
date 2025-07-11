include .env
export

# cpp compile configurations
CC := gcc
CXX := g++
CXXFLAGS := -std=c++17 -pthread -Wall -Wextra -Werror
INCLUDES := -isystem $(GTEST_DIR)/googletest/include
LIBS := $(GTEST_DIR)/build/lib/libgtest.a $(GTEST_DIR)/build/lib/libgtest_main.a

SRC ?=
BIN := $(basename $(SRC)).out
EXT := $(suffix $(SRC))

.PHONY: all cpp clean

all: $(EXT)

.cpp:
ifeq ($(origin SRC), command line)
	$(info SRC=$(SRC))
else
	$(error SRC is not set, please provide a source file to compile (e.g. make SRC=your_file.cpp))
endif
	$(CXX) $(SRC) $(CXXFLAGS) -o $(BIN) $(INCLUDES) $(LIBS)

clean:
	rm -rf $(BIN_DIR)/