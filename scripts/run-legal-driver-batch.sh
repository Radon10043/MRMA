#!/bin/bash

# Check legality and run test drivers in batches

source ./scripts/utils.sh

ROOTDIR=
RUN_DRIVER_SH=$(realpath $(dirname $0)/run-driver.sh)
DEVNULL=/dev/null

# Print help message
function print_help() {
    echo
    echo "Usage: $0 [ARGS]"
    echo "  Args (Required):"
    echo "    -p, --path <ROOTDIR>  The root directory to search for test_driver files."
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
echo "sut,path,legality,test_result"
for f in $(find $ROOTDIR -name test_driver* | sort); do
    if [ $(basename $f) == "test_driver.out" ]; then
        continue
    fi
    sut=$(get_sut_name $f)

    # Check legality
    legality="unknown"
    if [ -d $f ]; then
        legality=$(python3 -m src.legal -f $f/test/DriverTest.java)
    else
        legality=$(python3 -m src.legal -f $f)
    fi
    retval=$?
    if [ $retval -ne 0 ]; then
        legality="error"
    fi

    # Run test driver
    test_res=""
    $RUN_DRIVER_SH --driver $f >$DEVNULL
    exit_code=$?
    case $exit_code in
    0)
        test_res="PASS"
        ;;
    124)
        test_res="TIMEOUT"
        ;;
    *)
        test_res="FAILED"
        ;;
    esac
    echo "$sut,$f,$legality,$test_res"
done
