"""
Author       : Radon
Date         : 2025-12-16 20:53:06
LastEditors  : Radon
LastEditTime : 2025-12-17 20:32:36
Description  : A helper script for MRC legality checks
"""

import argparse
import ast
import pathlib
import subprocess

import javalang.parse
import javalang.tree
from clang.cindex import Config, Cursor, CursorKind, Index

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

INTEREST_FUNCS_JAVA = {
    "feeCalculation",  # ACMS
    "indexOf",  # Boyer
    "phoneBillCalculation",  # CUBS
    "determinant",  # Determinant1
    "calculateReimbursementAmount",  # ERS
    "det",  # JAMA
    "fullTextSearch",  # Lucene
    "maximalRectangle",  # MaxRectangle
    "max_sub",  # Maxsub
    "generateMSR",  # MOS
    "shortest_superstring",  # Superstring
    "triangle_square",  # Trisquarej
}

INTEREST_IMPORTS_JAVA = {
    "com.alibaba.fastjson",  # fastjson
    "org.joda.time",  # jodatime
}

INTEREST_FUNCS_PYTHON = {
    "f_oneway",  # f_oneway
    "rotate",  # rotate
    "shortest_path", # shortest_path
    # Following are interest funcs for grep, Printtokens, Printtokens2, schedule,
    # shcedule2, and TCAS
    "popen",
    "check_output",
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


class CppResolver:
    def __init__(self):
        pass

    def check_legal(self, filepath: pathlib.Path) -> bool:
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
        callee_dict = dict()

        def dfs(node: Cursor):
            if node.location.is_in_system_header:
                return
            if node.kind == CursorKind.CALL_EXPR:
                func_name = node.spelling
                callee_dict[func_name] = callee_dict.get(func_name, 0) + 1
            for child in node.get_children():
                dfs(child)

        dfs(tu.cursor)

        # If any of the interest functions are called twice or more, we consider the MRC
        # to be legal. This may not be precise in some cases but for reference is enough.
        for func in INTEREST_FUNCS_CPP:
            if callee_dict.get(func, 0) >= 2:
                return True
        return False


class JavaResolver:
    def __init__(self):
        pass

    def get_var_type(self, root: javalang.tree.MethodDeclaration, name: str) -> str | None:
        """Get type of given variable

        Parameters
        ----------
        root : java.tree.MethodDeclaration
            Root node of method declaration
        name : str
            Variable name

        Returns
        -------
        str | None
            Variable type if name can be found, else None
        """
        # Check local variable declarations
        for _, node in root.filter(javalang.tree.LocalVariableDeclaration):
            for _, decl in node.filter(javalang.tree.VariableDeclarator):
                var_type = getattr(getattr(node, "type", None), "name", None)
                var_name = getattr(decl, "name", None)
                if name == var_name:
                    return var_type

        # Check method parameters
        params = getattr(root, "parameters", None)
        if params is None:
            return None
        for param in params:
            param_type = getattr(getattr(param, "type", None), "name", None)
            param_name = getattr(param, "name", None)
            if name == param_name:
                return param_type
        return None

    def check_legal(self, filepath: pathlib.Path) -> bool:
        """Check legality of an encoded MRC written in Java

        Parameters
        ----------
        filepath : pathlib.Path
            Path to the Java file

        Returns
        -------
        bool
            True if legal, False otherwise
        """
        code = filepath.read_text()
        tree = javalang.parse.parse(code)
        callee_dict = dict()  # {qualifier.member: count}
        vars = list()
        for _, node in tree.filter(javalang.tree.MethodInvocation):
            qualifier = getattr(node, "qualifier")
            member = getattr(node, "member")
            key = f"{qualifier}.{member}"
            callee_dict[key] = callee_dict.get(key, 0) + 1
            if qualifier and qualifier != "":
                vars.append(qualifier)

        # If any of the interest functions are called twice or more from same qualifier,
        # we consider the MRC to be legal. This may not be precise in some cases but for
        # reference is enough.
        func_dict = dict()
        for func in INTEREST_FUNCS_JAVA:
            for k, v in callee_dict.items():
                if k.endswith(func):
                    func_dict[func] = func_dict.get(func, 0) + v
        for _, v in func_dict.items():
            if v >= 2:
                return True

        # For complex cases like fastjson and jodatime, we check source of qualifier and
        # call count. If source imports is interested and call count >= 2, we consider legal.
        # First let's collect used variable types
        var_types = list()
        for var in vars:
            var_type = None
            for _, node in tree.filter(javalang.tree.MethodDeclaration):
                if not isinstance(node, javalang.tree.MethodDeclaration):
                    continue
                var_type = self.get_var_type(node, var)
                if not var_type is None:
                    break
            var_types.append(var_type if not var_type is None else var)

        # Map used variable types to imports
        import_dict = dict()  # {import name: call count}
        for _, node in tree.filter(javalang.tree.Import):
            import_name = getattr(node, "path", None)
            if import_name is None:
                continue
            for var_type in var_types:
                if import_name.endswith(var_type):
                    import_dict[import_name] = import_dict.get(import_name, 0) + 1

        # Check legality
        for imp in INTEREST_IMPORTS_JAVA:
            for k, v in import_dict.items():
                if k.startswith(imp) and v >= 2:
                    return True
        return False


class PythonAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.callee_dict = dict()  # {callee name: count}

    def visit_Call(self, node: ast.Call):
        """Visit call node

        Parameters
        ----------
        node : ast.Call
            Call node
        """
        callee = self.get_func_name(node)
        if callee is not None:
            self.callee_dict[callee] = self.callee_dict.get(callee, 0) + 1
        self.generic_visit(node)

    def get_func_name(self, node: ast.Call) -> str | None:
        """Get function name from call node

        Parameters
        ----------
        node : ast.Call
            Call node

        Returns
        -------
        str | None
            Function name if found, else None
        """
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None


class PythonResolver:
    def __init__(self):
        pass

    def check_legal(self, filepath: pathlib.Path) -> bool:
        """Check legality of an encoded MRC written in Python

        Parameters
        ----------
        filepath : pathlib.Path
            Path to the Python file

        Returns
        -------
        bool
            True if legal, False otherwise
        """
        code = filepath.read_text()
        callee_dict = dict()
        tree = ast.parse(code)
        pa = PythonAnalyzer()
        pa.visit(tree)
        callee_dict = pa.callee_dict
        for func in INTEREST_FUNCS_PYTHON:
            if callee_dict.get(func, 0) >= 2:
                return True
        return False


def main(args: argparse.Namespace):
    """Main function to check legality of MR

    Parameters
    ----------
    args : argparse.Namespace
        _description_
    """
    if not check_config(args):
        FATAL("args are invalid")

    # Dispatch legality check based on file extension
    jr = JavaResolver()
    cr = CppResolver()
    pr = PythonResolver()
    legal_func_dict = {
        ".cpp": cr.check_legal,
        ".java": jr.check_legal,
        ".py": pr.check_legal,
    }
    filepath = pathlib.Path(args.file)
    if not filepath.suffix in legal_func_dict.keys():
        FATAL(f"File type {filepath.suffix} is not supported")
    if legal_func_dict[filepath.suffix](filepath):
        SAYF("LEGAL\n")
    else:
        SAYF("ILLEGAL\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A helper script for MR legality checks (for reference only)")
    parser.add_argument("-f", "--file", type=str, required=True, help="Path to the file to check")
    args = parser.parse_args()
    main(args)
