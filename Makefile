include .env
export

# General configurations
BIN := $(basename $(SRC)).out
EXT := $(suffix $(SRC))
REP ?= 20
TIMEOUT ?= 5
VERBOSE?=0

# Conditionally set output redirection based on VERBOSE
ifeq ($(VERBOSE), 0)
    REDIRECT = > /dev/null 2>&1
else
    REDIRECT =
endif

# cpp compile configurations
CXX := g++
CXXFLAGS := -std=c++17 -static -pthread -Wall -Wextra -Werror
INCLUDES := -isystem $(GTEST_DIR)/googletest/include
LIBS := $(GTEST_DIR)/build/lib/libgtest.a $(GTEST_DIR)/build/lib/libgtest_main.a

# java compile configurations
JAVA := java
JAVAC := javac
JAVAFLAGS := -cp "$(JAVAPROJ)/bin:$(JAVAPROJ)/lib/*" org.junit.platform.console.ConsoleLauncher -disable-ansi-colors --scan-class-path
JAVACFLAGS := -d $(JAVAPROJ)/bin -cp "$(JAVAPROJ)/lib/*"
JAVATEST := $(JAVAPROJ)/test/DriverTest.java
JAVASRCDIR := $(JAVAPROJ)/src

# python configurations
# Not yet :)

# SIR test set configurations
SIR_CC := gcc
SIR_CFLAGS := -std=c17 -static -O2
PT_DIR := $(PROJECT)/Empirical-Study-LLM-MR/software-under-test/Printtokens/src
PT2_DIR := $(PROJECT)/Empirical-Study-LLM-MR/software-under-test/Printtokens2/src
SCD_DIR := $(PROJECT)/Empirical-Study-LLM-MR/software-under-test/schedule/src
SCD2_DIR := $(PROJECT)/Empirical-Study-LLM-MR/software-under-test/schedule2/src
GREP_DIR := $(PROJECT)/Empirical-Study-LLM-MR/software-under-test/grep/src
TCAS_DIR := $(PROJECT)/Empirical-Study-LLM-MR/software-under-test/TCAS/src

.PHONY: all clean build_cpp build_java build_python build_sir build_printtokens build_printtokens2 build_schedule build_schedule2 build_grep build_tcas run_cpp run_java run_python download patch

build_cpp:
ifndef SRC
	$(error SRC is not set, please provide a source file to compile (e.g. make SRC=your_file.cpp build_cpp))
endif
	$(CXX) $(SRC) $(CXXFLAGS) -o $(BIN) $(INCLUDES) $(LIBS)

build_java:
ifndef JAVAPROJ
	$(error JAVAPROJ is not set, please provide a source file to compile (e.g. make JAVAPROJ=./test_driver_java build_java))
endif
	find $(JAVASRCDIR) -name "*.java" | xargs $(JAVAC) $(JAVACFLAGS) $(JAVATEST) 2> /tmp/build_java.log

build_python:
	@echo "No need to build Python program, just run 'make PYTHON=your_file.py run_python'"

build_printtokens:
	@echo -n "Building Printtokens ... "
	@$(SIR_CC) $(SIR_CFLAGS) $(PT_DIR)/print_tokens.c $(PT_DIR)/stream.h $(PT_DIR)/tokens.h -o $(PT_DIR)/print_tokens.out 2> /tmp/build_sir.log
	@echo "OK"

build_printtokens2:
	@echo -n "Building Printtokens2 ... "
	@$(SIR_CC) $(PT2_DIR)/print_tokens2.c $(PT2_DIR)/stream.h $(PT2_DIR)/tokens.h -o $(PT2_DIR)/print_tokens2.out 2> /tmp/build_sir.log
	@echo "OK"

build_schedule:
	@echo -n "Building schedule ... "
	@$(SIR_CC) $(SIR_CFLAGS) $(SCD_DIR)/schedule.c -o $(SCD_DIR)/schedule.out 2> /tmp/build_sir.log
	@echo "OK"

build_schedule2:
	@echo -n "Building schedule2 ... "
	@$(SIR_CC) $(SIR_CFLAGS) $(SCD2_DIR)/schedule2.c $(SCD2_DIR)/schedule2.h -o $(SCD2_DIR)/schedule2.out 2> /tmp/build_sir.log
	@echo "OK"

build_grep:
	@echo -n "Building grep ... "
	@cd $(GREP_DIR) && \
		./build.sh > /tmp/build_sir.log 2>&1 && \
		cd - > /dev/null
	@echo "OK"

build_tcas:
	@echo -n "Building TCAS ... "
	@$(SIR_CC) $(SIR_CFLAGS) $(TCAS_DIR)/tcas.c -o $(TCAS_DIR)/tcas.out 2> /tmp/build_sir.log
	@echo "OK"

build_sir: build_printtokens build_printtokens2 build_schedule build_schedule2 build_grep build_tcas
	@echo "Finished building all SIR programs."

run_cpp:
ifndef BIN
	$(error BIN is not set, please provide a source file to compile (e.g. make BIN=your_file.out run_cpp))
endif
	@echo "--- Starting Repetitive Run ---"
	@echo "Binary: $(BIN)"
	@echo "Repetitions: $(REP)"
	@echo "Timeout: $(TIMEOUT) seconds"
	@echo "-------------------------------"
	@for i in $$(seq $(REP)); do \
		echo -n "Running iteration $$i ..."; \
		if timeout $(TIMEOUT) $(BIN) $(REDIRECT); then \
			echo " OK"; \
		else \
			exit_code=$$?; \
			if [ $$exit_code -eq 124 ]; then \
				echo " TIMEOUT! Stopping execution."; \
			else \
				echo " FAILED! Stopping execution."; \
			fi; \
			echo "-------------------------------";\
			exit $$exit_code; \
		fi; \
	done
	@echo "-------------------------------"
	@echo "Successfully completed all $(REP) runs."

run_java:
ifndef JAVAPROJ
	$(error JAVAPROJ is not set, please provide a source file to compile (e.g. make JAVAPROJ=./test_driver_java run_java))
endif
	@echo "--- Starting Repetitive Run ---"
	@echo "Java Project: $(JAVAPROJ)"
	@echo "Repetitions: $(REP)"
	@echo "Timeout: $(TIMEOUT) seconds"
	@echo "-------------------------------"
	@for i in $$(seq $(REP)); do \
		echo -n "Running iteration $$i ..."; \
		if timeout $(TIMEOUT) $(JAVA) $(JAVAFLAGS) $(REDIRECT); then \
			echo " OK"; \
		else \
			exit_code=$$?; \
			if [ $$exit_code -eq 124 ]; then \
				echo " TIMEOUT! Stopping execution."; \
			else \
				echo " FAILED! Stopping execution."; \
			fi; \
			echo "-------------------------------";\
			exit 1; \
		fi; \
	done
	@echo "-------------------------------"
	@echo "Successfully completed all $(REP) runs."

run_python:
ifndef PYTHON
	$(error PYTHON is not set, please provide a source file to run (e.g. make PYTHON=your_file.py run_python))
endif
	@echo "--- Starting Repetitive Run ---"
	@echo "Python File: $(PYTHON)"
	@echo "Repetitions: $(REP)"
	@echo "Timeout: $(TIMEOUT) seconds"
	@echo "-------------------------------"
	@for i in $$(seq $(REP)); do \
		echo -n "Running iteration $$i ..."; \
		if timeout $(TIMEOUT) python3 $(PYTHON) $(REDIRECT); then \
			echo " OK"; \
		else \
			exit_code=$$?; \
			if [ $$exit_code -eq 124 ]; then \
				echo " TIMEOUT! Stopping execution."; \
			else \
				echo " FAILED! Stopping execution."; \
			fi; \
			echo "-------------------------------";\
			exit 1; \
		fi; \
	done
	@echo "-------------------------------"
	@echo "Successfully completed all $(REP) runs."

download:
	@mkdir -p downloads
	@wget -P downloads -nc \
		https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar \
		https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.10.0/junit-platform-console-standalone-1.10.0.jar \
		https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.14.0/commons-lang3-3.14.0.jar \
		https://repo1.maven.org/maven2/com/alibaba/fastjson/1.2.83/fastjson-1.2.83.jar \
		https://repo1.maven.org/maven2/com/alibaba/fastjson/1.2.83/fastjson-1.2.83-sources.jar

check:
	@python3 -m src.check --out check.log
	@echo "Check completed, see details in check.log"

patch_sut:
	@echo -n "Applying patches ... "
	@git -C Empirical-Study-LLM-MR apply $(PWD)/patch/sut.patch
	@echo "OK."

restore_sut:
	@echo -n "Restoring submodules ... "
	@git -C Empirical-Study-LLM-MR checkout . 2> /dev/null
	@git -C Empirical-Study-LLM-MR clean -fd 2> /dev/null
	@echo "OK."

clean:
	rm -f $(PT_DIR)/print_tokens.out
	rm -f $(PT2_DIR)/print_tokens2.out
	rm -f $(SCD_DIR)/schedule.out
	rm -f $(SCD2_DIR)/schedule2.out
	rm -f $(TCAS_DIR)/tcas.out
	rm -f check.log
	cd $(GREP_DIR) && rm -rf grep-3.11 && cd - > /dev/null

cleantmp:
	rm -rf /tmp/test_driver*
