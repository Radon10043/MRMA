#!/bin/bash

# Build and run a single test driver (C++, Java, Python) with options
# for timeout, verbosity, and repetitions.

source .env

DRIVER=           # Path to test driver
TIMEOUT=5         # Timeout in seconds for each test driver
VERBOSE=0         # Verbose mode
REPEAT=20         # Number of repetitions for each test driver

# Print help message
print_help() {
	echo
	echo "Usage: $0 [ARGS]"
	echo "  Args (Required):"
	echo "    -d, --driver <DRIVER>    The path to the test_driver file."
	echo "  Args (Optional):"
	echo "    -t, --timeout <TIMEOUT>  The timeout for each test driver (default: $TIMEOUT seconds)."
	echo "    -v, --verbose            Enable verbose mode (default: disable)."
	echo "    -r, --repeat <REPEAT>    The number of repetitions for each test driver (default: $REPEAT)."
	echo "    -h, --help               Show help message."
	echo
}

# Build C++ test driver
build_cpp() {
	local SRC=$1
	local CXX=g++
	local CXXFLAGS="-std=c++17 -static -pthread -Wall -Wextra -Werror"
	local INCLUDES="-isystem $GTEST_DIR/googletest/include"
	local LIBS="$GTEST_DIR/build/lib/libgtest.a $GTEST_DIR/build/lib/libgtest_main.a"
	local BIN="$(dirname $SRC)/$(basename $SRC .cpp).out"
	eval $CXX $SRC $CXXFLAGS -o $BIN $INCLUDES $LIBS
}

# Run C++ test driver
run_cpp() {
	local BIN=$1
	eval timeout --foreground $TIMEOUT $BIN
}

# Build Java test driver
build_java() {
	local JAVAPROJ=$1
	local JAVAC="javac"
	local JAVACFLAGS="-d $JAVAPROJ/bin -cp \"$JAVAPROJ/lib/*\""
	local JAVATEST="$JAVAPROJ/test/DriverTest.java"
	local JAVASRCDIR="$JAVAPROJ/src"
	eval $JAVAC $JAVACFLAGS $JAVATEST $(find $JAVASRCDIR -name "*.java")
}

# Run Java test driver
run_java() {
	local JAVAPROJ=$1
	local JAVA=java
	local JAVAFLAGS="-cp \"$JAVAPROJ/bin:$JAVAPROJ/lib/*\" org.junit.platform.console.ConsoleLauncher -disable-ansi-colors --scan-class-path"
	eval timeout --foreground $TIMEOUT $JAVA $JAVAFLAGS
}

run_python() {
	eval timeout --foreground $TIMEOUT python3 $DRIVER
}

# Analyze arguments
if [ $# -eq 0 ]; then
	print_help
	exit 1
fi
while [[ $# -gt 0 ]]; do
	case $1 in
	-h | --help)
		print_help
		exit 0
		;;
	-d | --driver)
		DRIVER=$2
		shift 2
		;;
	-t | --timeout)
		TIMEOUT=$2
		shift 2
		;;
	-v | --verbose)
		VERBOSE=1
		shift
		;;
	-r | --repeat)
		REPEAT=$2
		shift 2
		;;
	*)
		print_help
		exit 1
		;;
	esac
done
# Conditionally set output redirection based on VERBOSE
if [ $VERBOSE -eq 0 ]; then
	REDIRECT="> $DEVNULL 2>&1"
else
	REDIRECT=
fi

# Build
exit_code=0
case $(basename $DRIVER) in
# cpp
test_driver.cpp)
	build_cpp $DRIVER
	exit_code=$?
	BIN=$(dirname $DRIVER)/test_driver.out
	;;
# java
test_driver)
	build_java $DRIVER
	exit_code=$?
	JAVAPROJ=$DRIVER
	;;
# python
test_driver.py)
	# Nothing to do :)
	;;
*)
	echo "Unsupported test driver: $DRIVER"
	exit 1
	;;
esac
if [ $exit_code -ne 0 ]; then
	echo "Build failed for $DRIVER"
	exit 1
fi

# Run test driver
echo "--- Starting Repetitive Run ---"
echo "Driver: $DRIVER"
echo "Repetitions: $REPEAT"
echo "Timeout: $TIMEOUT seconds"
echo "-------------------------------"
for i in $(seq 1 $REPEAT); do
	output=""
	res=""
	exit_code=0
	echo -n "Running iteration $i ..."
	case $(basename $DRIVER) in
	# cpp
	test_driver.cpp)
		output=$(run_cpp $BIN 2>&1)
		;;
	# java
	test_driver)
		output=$(run_java $JAVAPROJ 2>&1)
		;;
	# python
	test_driver.py)
		output=$(run_python $DRIVER 2>&1)
		;;
	*)
		echo "Unsupported test driver: $DRIVER"
		exit 1
		;;
	esac
	exit_code=$?
	if [ $exit_code -ne 0 ]; then
		case $exit_code in
		124)
			echo " TIMEOUT! Stop execution."
			;;
		*)
			echo " FAILED! Stop execution."
			;;
		esac
	else
		echo " OK"
	fi
	if [ $VERBOSE -eq 1 ]; then
		echo
		echo "######"
		echo "Output:"
		echo "######"
		echo
		echo "$output"
	fi
	if [ $exit_code -ne 0 ]; then
		exit $exit_code
	fi
done
