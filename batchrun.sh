#!/bin/bash

root_dir=$1
ext=$2

for f in $(ls $root_dir); do
    echo -n "Testing $root_dir/$f ... "
    output=""
    exit_code=0
    case $ext in
        cpp)
            output=$(make SRC=$root_dir/$f/test_driver.cpp BIN=$root_dir/$f/test_driver.out build_cpp run_cpp 2>&1)
            ;;
        java)
            output=$(make JAVAPROJ=$root_dir/$f/test_driver run_java 2>&1)
            ;;
        py)
            output=$(make PYTHON=$root_dir/$f/test_driver.py run_python 2>&1)
            ;;
        *)
            echo "Unsupported extension: $ext"
            exit 1
            ;;
    esac
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        err=$(($(echo $output | tail -n 1 | awk -F 'Error ' '{print $2}')))
        case $err in
            124)
                echo "TIMEOUT"
                ;;
            *)
                echo "FAILED: $err"
        esac
    else
        echo "OK"
    fi
done