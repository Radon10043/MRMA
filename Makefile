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
REP ?= 5

.PHONY: all cpp clean

all: $(EXT)

.cpp:
ifneq ($(origin SRC), command line)
	$(error SRC is not set, please provide a source file to compile (e.g. make SRC=your_file.cpp))
endif
	$(CXX) $(SRC) $(CXXFLAGS) -o $(BIN) $(INCLUDES) $(LIBS)

run:
	@echo "--- Starting Repetitive Run ---"
	@echo "Binary: $(BIN)"
	@echo "Repetitions: $(REP)"
	@echo "-------------------------------"
	@for i in $$(seq $(REP)); do \
		echo -n "Running iteration $$i ..."; \
		if ./$(BIN) > /dev/null 2>&1; then \
			echo " OK"; \
		else \
			echo " FAILED! Stopping execution."; \
			exit 1; \
		fi; \
	done
	@echo "-------------------------------"
	@echo "Successfully completed all $(REP) runs."

clean:
	rm -rf $(BIN_DIR)/