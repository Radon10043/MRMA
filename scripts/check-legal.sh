#!/bin/bash

ROOTDIR=

# Print help message
print_help() {
    echo
    echo "Usage: $0 [ARGS]"
    echo "  Args (Required):"
    echo "    -p, --path <ROOTDIR>  The root directory to search for test_driver.cpp, test_driver.py, and DriverTest.java."
    echo "  Args (Optional):"
    echo "    -h, --help:           Show help message."
    echo
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
    -p | --path)
        ROOTDIR=$(realpath $2)
        shift 2
        ;;
    *)
        print_help
        exit 1
        ;;
    esac
done

# Run test drivers in batches
echo "path,legality"
for f in $(find $ROOTDIR -type f \( -name test_driver.cpp -o -name test_driver.py -o -name DriverTest.java \) | sort); do
    res=""
    output=$(python3 -m src.legal -f $f)
    retval=$?
    if [ $retval -ne 0 ]; then
        res="error"
    else
        res=$output
    fi
    echo "$f,$res"
done
