"""
Author       : Radon
Date         : 2025-07-20 02:34:17
LastEditors  : Radon
LastEditTime : 2025-07-20 06:43:19
Description  : Check the quality of configs in $PROJECT/configs.
"""

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from utils import *

# Error codes & corresponding messages
EAPILEAK = 0b00000001  # API key or base URL is leaked
EABSPATH = 0b00000010  # Absolute path exists
ESTRGNUM = 0b00000100  # max_MRs is too small (< 5) or too large (> 40)
EEXISTMR = 0b00001000  # existing_mrs is not empty or not a list
EEXTRDEP = 0b00010000  # External corpus, specification, example_mr, and example_analysis are not consistent
ESUTNAME = 0b00100000  # sut_name is not consistent with external corpus, specification, etc.
EUNKWSUT = 0b01000000  # sut_name is not in the SUT_NAMES dictionary

ERROR_MESSAGES = {
    EAPILEAK: "API key or base URL is leaked",
    EABSPATH: "Absolute path exists",
    ESTRGNUM: "max_MRs is too small (< 5) or too large (> 40)",
    EEXISTMR: "existing_mrs is not empty or not a list",
    EEXTRDEP: "External corpus, specification, example_mr, and example_analysis are not consistent",
    ESUTNAME: "sut_name is not consistent with external corpus, specification, etc.",
    EUNKWSUT: "sut_name is not in the SUT_NAMES dictionary",
}

# Dictionary to map sut abbreviations to full names
# fmt:off
SUT_NAMES = {
    "ACMS"                 : "Aviation Consignment Management System",
    "Boyer"                : "Boyer-Moore algorithm",
    "Bsearch1"             : "Get Range Algorithm",
    "Bsearch2"             : "Binary Search Algorithm",
    "ClosestPair"          : "Closest Distance Algorithm",
    "CUBS"                 : "China Unicom Billing System",
    "Determinant1"         : "Michael Thomas Flanagan's Library",
    "DistinctSubsequence"  : "Number of Distinct Subsequences Calculation Algorithm",
    "Editingdistance"      : "Editing Distance Calculation Algorithm",
    "ERS"                  : "Expense Reimbursement System",
    "f_oneway"             : "One-way ANOVA",
    "FastJson"             : "FastJson",
    "FirstMissingPositive" : "Smallest Positive Integer Finding Algorithm",
    "grep"                 : "grep",
    "HeapSort"             : "Heap Sort Algorithm",
    "InterleavingString"   : "Interleaved String Checking Algorithm",
    "JAMA"                 : "Java Matrix Package JAMA",
    "Jodatime"             : "Jodatime",
    "Klp"                  : "Key-lock Problem",
    "Lucene"               : "Text Search Engine Lucene",
    "MaxRectangle"         : "Largest Area of Rectangle Calculation Algorithm",
    "Maxsub"               : "Maximum Subarray Sum Calculation Algorithm",
    "MOS"                  : "Meal Ordering System",
    "Multi-MAXSUM"         : "Maximum Sum of Multiple Contiguous, Non-overlapping Subarrays Calculation Algorithm",
    "Printtokens"          : "Lexical analyzer print_tokens",
    "Printtokens2"         : "Lexical analyzer print_tokens2",
    "QuickSort"            : "Quick Sort Algorithm",
    "rotate"               : "rotate function from scipy.ndimage",
    "RSA"                  : "RSA Algorithm",
    "schedule"             : "Priority scheduler",
    "schedule2"            : "Priority scheduler",
    "shortest_path"        : "shortest_path function from scipy.sparse.csgraph",
    "Spwiki"               : "Shortest Path Distance Calculation Algorithm",
    "Superstring"          : "The Shortest Superstring Identification Algorithm",
    "SurroundedRegion"     : "Surrounded Region Identification Algorithm",
    "TCAS"                 : "Traffic Collision Avoidance System",
    "Trisquarej"           : "Triangle Area and Type Identification Algorithm",
}
# fmt:on


def check(cfg: dict) -> int:
    """Check the

    Parameters
    ----------
    cfg : dict
        Configuration dictionary to check.

    Returns
    -------
    int
        Error codes indicating the quality issues found in the config.
    """
    res = 0
    external_deps = set()
    sut_name = str()

    # Traverse function for config checking
    def dfs(dt: dict):
        nonlocal res, sut_name
        for k, v in dt.items():
            if k in ["external_corpus", "specification", "example_mr", "example_analysis"]:
                external_deps.add(os.path.basename(v))
            elif k == "sut_name":
                sut_name = v
            elif k == "max_MRs" and (v < 5 or v > 40):
                res |= ESTRGNUM
            elif k == "existing_mrs":
                if not isinstance(v, list) or len(v) > 0:
                    res |= EEXISTMR
            elif isinstance(v, str):
                if k in ["api_key", "base_url"]:
                    res |= EAPILEAK
                if os.path.isabs(v):
                    res |= EABSPATH
            elif isinstance(v, dict):
                dfs(v)
            elif isinstance(v, list):
                for elem in v:
                    dfs(elem) if isinstance(elem, dict) else None

    # Check the quality of the config
    dfs(cfg)
    if len(external_deps) > 1:
        res |= EEXTRDEP
    elif len(external_deps) == 1:
        abbr = os.path.splitext(next(iter(external_deps)))[0]
        res |= ESUTNAME if sut_name != SUT_NAMES.get(abbr) else 0
        res |= EUNKWSUT if abbr not in SUT_NAMES else 0

    return res


def print_report(res_dict: dict, out_file: str):
    """Print the report of the check results.

    Parameters
    ----------
    res_dict : dict
        Dictionary containing the results of the checks, where keys are config file paths and values are error codes.
    out_file : str
        Output file to save the report. If None, print to stdout.
    """
    header = "=" * 20 + " [Checking Report] " + "=" * 20
    split_line = "=" * (len(header))
    report = header + "\n"
    if len(res_dict) == 0:
        report += "No issues found, nice!\n"
        report += split_line + "\n"
    for config, errors in res_dict.items():
        report += f"Config: {config}\n"
        report += f"Errors (0x{errors:b}):\n"
        for code, message in ERROR_MESSAGES.items():
            if errors & code:
                report += f"  - {message}\n"
        report += split_line + "\n"
    if out_file:
        Path(out_file).write_text(report, encoding="utf-8")
    else:
        SAYF(report)


def main(args: argparse.Namespace):
    """Main function to check whether sensitive information is leaked in configs.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments, including output file for the report.
    """
    # Get project path
    load_dotenv()
    project_path = os.getenv("PROJECT")
    if not project_path:
        FATAL("PROJECT environment variable is not set.")

    # Get all configs
    configs_path = os.path.join(project_path, "configs")  # type: ignore
    configs = list()
    for root, _, files in os.walk(configs_path):
        if os.path.basename(root) == "template":
            continue
        for file in files:
            if file.endswith(".json"):
                configs.append(os.path.join(root, file))
    configs.sort()

    # Traverse each config, check whether sensitive info is leaked
    res_dict = dict()
    for config in configs:
        s = Path(config).read_text(encoding="utf-8")
        cfg = json.loads(s)
        SAYF(f"Checking {config} ... ")
        res = check(cfg)
        if res:
            res_dict[config] = res
            SAYF(f"ERROR: {res} (0x{res:b})\n")
        else:
            SAYF("OK.\n")

    # Print the report
    print_report(res_dict, args.out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check the quality of configs in $PROJECT/configs.")
    parser.add_argument("--out", type=str, default=None, help="Output file to save the report")
    args = parser.parse_args()
    main(args)
