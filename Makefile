include .env
export

# General configurations
SRC ?=
BIN := $(basename $(SRC)).out
EXT := $(suffix $(SRC))
REP ?= 5
TIMEOUT ?= 5

# cpp compile configurations
CXX := g++
CXXFLAGS := -std=c++17 -pthread -Wall -Wextra -Werror
INCLUDES := -isystem $(GTEST_DIR)/googletest/include
LIBS := $(GTEST_DIR)/build/lib/libgtest.a $(GTEST_DIR)/build/lib/libgtest_main.a

# java compile configurations
JAVAPROJ ?=
JAVA := java
JAVAC := javac
JAVAFLAGS := -cp "$(JAVAPROJ)/bin:$(JAVAPROJ)/lib/*" org.junit.platform.console.ConsoleLauncher --scan-class-path
JAVACFLAGS := -d $(JAVAPROJ)/bin -cp "$(JAVAPROJ)/lib/*"
JAVASRC := $(JAVAPROJ)/test/DriverTest.java

# python configurations
PYTHON ?=

.PHONY: all cpp clean

build_cpp:
ifneq ($(origin SRC), command line)
	$(error SRC is not set, please provide a source file to compile (e.g. make SRC=your_file.cpp build_cpp))
endif
	$(CXX) $(SRC) $(CXXFLAGS) -o $(BIN) $(INCLUDES) $(LIBS)

build_java:
ifneq ($(origin JAVAPROJ), command line)
	$(error JAVAPROJ is not set, please provide a source file to compile (e.g. make JAVAPROJ=./test_driver_java build_java))
endif
	$(JAVAC) $(JAVACFLAGS) $(JAVASRC)

build_python:
	@echo "No need to build Python program, just run 'make PYTHON=your_file.py run_python'"

run_cpp:
ifneq ($(origin BIN), command line)
	$(error BIN is not set, please provide a source file to compile (e.g. make BIN=your_file.out run_cpp))
endif
	@echo "--- Starting Repetitive Run ---"
	@echo "Binary: $(BIN)"
	@echo "Repetitions: $(REP)"
	@echo "Timeout: $(TIMEOUT) seconds"
	@echo "-------------------------------"
	@for i in $$(seq $(REP)); do \
		echo -n "Running iteration $$i ..."; \
		if timeout $(TIMEOUT) ./$(BIN) > /dev/null 2>&1; then \
			echo " OK"; \
		else \
			exit_code=$$?; \
			if [ $$exit_code -eq 124 ]; then \
				echo " TIMEOUT! Stopping execution."; \
			else \
				echo " FAILED! Stopping execution."; \
			fi; \
			exit 1; \
		fi; \
	done
	@echo "-------------------------------"
	@echo "Successfully completed all $(REP) runs."

run_java:
ifneq ($(origin JAVAPROJ), command line)
	$(error JAVAPROJ is not set, please provide a source file to compile (e.g. make JAVAPROJ=./test_driver_java run_java))
endif
	@echo "--- Starting Repetitive Run ---"
	@echo "Java Project: $(JAVAPROJ)"
	@echo "Repetitions: $(REP)"
	@echo "Timeout: $(TIMEOUT) seconds"
	@echo "-------------------------------"
	@for i in $$(seq $(REP)); do \
		echo -n "Running iteration $$i ..."; \
		if timeout $(TIMEOUT) $(JAVA) $(JAVAFLAGS) > /dev/null 2>&1; then \
			echo " OK"; \
		else \
			exit_code=$$?; \
			if [ $$exit_code -eq 124 ]; then \
				echo " TIMEOUT! Stopping execution."; \
			else \
				echo " FAILED! Stopping execution."; \
			fi; \
			exit 1; \
		fi; \
	done
	@echo "-------------------------------"
	@echo "Successfully completed all $(REP) runs."

run_python:
ifneq ($(origin PYTHON), command line)
	$(error PYTHON is not set, please provide a source file to run (e.g. make PYTHON=your_file.py run_python))
endif
	@echo "--- Starting Repetitive Run ---"
	@echo "Python File: $(PYTHON)"
	@echo "Repetitions: $(REP)"
	@echo "Timeout: $(TIMEOUT) seconds"
	@echo "-------------------------------"
	@for i in $$(seq $(REP)); do \
		echo -n "Running iteration $$i ..."; \
		if timeout $(TIMEOUT) python3 $(PYTHON) > /dev/null 2>&1; then \
			echo " OK"; \
		else \
			exit_code=$$?; \
			if [ $$exit_code -eq 124 ]; then \
				echo " TIMEOUT! Stopping execution."; \
			else \
				echo " FAILED! Stopping execution."; \
			fi; \
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

clean:
	rm -rf $(BIN_DIR)/