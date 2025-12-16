"""
Author       : Radon
Date         : 2025-12-16 20:53:06
LastEditors  : Radon
LastEditTime : 2025-12-16 22:02:33
Description  : A helper script for MRC legality checks
"""

import argparse
import pathlib
import subprocess

from clang.cindex import Index, Config, Cursor, CursorKind
from .utils import *

# ========== GLOBAL VARIABLES ==========
INTEREST_FUNCS_CPP = {
    "get_range",  # Bsearch1
    "bin_search",  # Bsearch2
    "closest_distance",  # ClosestPair
    "numDistinct",  # DistinctSubsequence
    "edit_dist",  # EditingDistance
    "first_missing_positive",  # FirstMissingPositive
    "heap_sort",  # HeapSort
    "is_interleaved",  # InterleavingString
    "KLP",  # Klp
    "multi_maxsum",  # Multi-MAXSUM
    "quick_sort",  # QuickSort
    "candp",  # RSA
    "shortest_path",  # Spwiki
    "surrounded_region",  # SurroundedRegion
}
# ======================================


def check_config(args: argparse.Namespace) -> bool:
    """Check validity of args

    Parameters
    ----------
    args : argparse.Namespace
        Parsed arguments

    Returns
    -------
    bool
        True if args are valid, False otherwise
    """
    if not pathlib.Path(args.file).exists():
        BADF(f"File {args.file} does not exist")
        return False
    return True


def legal_mrc_cpp(filepath: pathlib.Path) -> bool:
    """Check legality of an encoded MRC written in C++

    Parameters
    ----------
    filepath : pathlib.Path
        Path to the C++ file

    Returns
    -------
    bool
        True if legal, False otherwise
    """
    # Load libclang
    if not Config.loaded:
        libclang_path = subprocess.run("llvm-config-19 --libdir", shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
        Config.set_library_path(libclang_path)

    # Parse the C++ file and record function calls
    index = Index.create()
    tu = index.parse(filepath.as_posix())
    call_dict = dict()

    def dfs(node: Cursor):
        if node.location.is_in_system_header:
            return
        if node.kind == CursorKind.CALL_EXPR:
            func_name = node.spelling
            call_dict[func_name] = call_dict.get(func_name, 0) + 1
        for child in node.get_children():
            dfs(child)

    dfs(tu.cursor)

    # If any of the interest functions are called twice or more, we consider the MRC
    # to be legal. This may not be precise in some cases but for reference is enough.
    for func in INTEREST_FUNCS_CPP:
        if call_dict.get(func, 0) >= 2:
            return True
    return False


# TODO: Implement legal_mrc_py and legal_mrc_java


def main(args: argparse.Namespace):
    """Main function to check leagality of MR

    Parameters
    ----------
    args : argparse.Namespace
        _description_
    """
    if not check_config(args):
        FATAL("args are invalid")

    # Dispatch legality check based on file extension
    legal_func_dict = {
        ".cpp": legal_mrc_cpp,
    }
    filepath = pathlib.Path(args.file)
    if not filepath.suffix in legal_func_dict.keys():
        FATAL(f"File type {filepath.suffix} is not supported")
    if legal_func_dict[filepath.suffix](filepath):
        SAYF("legal\n")
    else:
        SAYF("illegal\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A helper script for MR legality checks (for reference only)")
    parser.add_argument("-f", "--file", type=str, required=True, help="Path to the file to check")
    args = parser.parse_args()
    main(args)
