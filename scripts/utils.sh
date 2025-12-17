#!/bin/bash

declare -A SUT

SUT["ACMS"]=1
SUT["Boyer"]=1
SUT["Bsearch1"]=1
SUT["Bsearch2"]=1
SUT["ClosestPair"]=1
SUT["CUBS"]=1
SUT["Determinant1"]=1
SUT["DistinctSubsequence"]=1
SUT["Editingdistance"]=1
SUT["ERS"]=1
SUT["f_oneway"]=1
SUT["FastJson"]=1
SUT["FirstMissingPositive"]=1
SUT["grep"]=1
SUT["HeapSort"]=1
SUT["InterleavingString"]=1
SUT["JAMA"]=1
SUT["Jodatime"]=1
SUT["Klp"]=1
SUT["Lucene"]=1
SUT["MaxRectangle"]=1
SUT["Maxsub"]=1
SUT["MOS"]=1
SUT["Multi-MAXSUM"]=1
SUT["Printtokens"]=1
SUT["Printtokens2"]=1
SUT["QuickSort"]=1
SUT["rotate"]=1
SUT["RSA"]=1
SUT["schedule"]=1
SUT["schedule2"]=1
SUT["shortest_path"]=1
SUT["Spwiki"]=1
SUT["Superstring"]=1
SUT["SurroundedRegion"]=1
SUT["TCAS"]=1
SUT["Trisquarej"]=1

# Get possible function name from a given path
function get_sut_name() {
    local path=$1
    while [[ "$path" != "/" ]]; do
        local base=$(basename $path)
        if [[ ${SUT[$base]} ]]; then
            echo $base
            return
        fi
        path=$(dirname $path)
    done
}