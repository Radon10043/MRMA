#!/bin/bash

ROOTDIR=
RUN_DRIVER_SH=$(realpath $(dirname $0)/run-driver.sh)
DEVNULL=/dev/null

# Print help message
print_help() {
    echo
    echo "Usage: $0 [ARGS]"
    echo "  Args (Required):"
    echo "    -p, --path <ROOTDIR>: The root directory to search for test_driver files."
    echo "  Args (Optional):"
    echo "    -h, --help: Show help message."
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
echo "path,test_result"
for f in $(find $ROOTDIR -name test_driver* | sort); do
    res=""
    $RUN_DRIVER_SH --driver $f >$DEVNULL
    exit_code=$?
    case $exit_code in
    0)
        res="PASS"
        ;;
    124)
        res="TIMEOUT"
        ;;
    *)
        res="FAILED"
        ;;
    esac
    echo "$f,$res"
done
