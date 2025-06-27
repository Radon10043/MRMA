"""
Author       : Radon
Date         : 2025-06-27 16:42:43
LastEditors  : Radon
LastEditTime : 2025-06-27 20:42:51
Description  : Utility functions
"""

import marko

from marko.md_renderer import MarkdownRenderer


#######################
### Terminal Colors ###
#######################
class TerminalColors:
    cBLK = "\033[0;30m"
    cRED = "\033[0;31m"
    cGRN = "\033[0;32m"
    cBRN = "\033[0;33m"
    cBLU = "\033[0;34m"
    cMGN = "\033[0;35m"
    cCYA = "\033[0;36m"
    cLGR = "\033[0;37m"
    cGRA = "\033[1;90m"
    cLRD = "\033[1;91m"
    cLGN = "\033[1;92m"
    cYEL = "\033[1;93m"
    cLBL = "\033[1;94m"
    cPIN = "\033[1;95m"
    cLCY = "\033[1;96m"
    cBRI = "\033[1;97m"
    cRST = "\033[0m"


###############################
### Debug & error functions ###
###############################
def SAYF(msg: str, verbose: bool = True):
    if verbose:
        print(msg, end="")


def WARNF(msg: str, verbose: bool = True):
    SAYF(TerminalColors.cYEL + "[!] " + TerminalColors.cRST + msg + "\n", verbose)


def ACTF(msg: str, verbose: bool = True):
    SAYF(TerminalColors.cLBL + "[*] " + TerminalColors.cRST + msg + "\n", verbose)


def OKF(msg: str, verbose: bool = True):
    SAYF(TerminalColors.cLGN + "[+] " + TerminalColors.cRST + msg + "\n", verbose)


def BADF(msg: str, verbose: bool = True):
    SAYF(TerminalColors.cLRD + "[-] " + TerminalColors.cRST + msg + "\n", verbose)


def FATAL(msg: str):
    SAYF(TerminalColors.cLRD + "[-] PROGRAM ABORT :  " + TerminalColors.cRST + msg + "\n")
    exit(1)


def PFATAL(msg: str):
    SAYF(TerminalColors.cLRD + "\n[-] SYSTEM ERROR : " + TerminalColors.cBRI + msg + TerminalColors.cRST + "\n")
    exit(1)


###############################
### Miscellaneous functions ###
###############################
def get_first_code_block(md_text: str) -> str:
    """Extract the first fenced code block from a Markdown text.

    Parameters
    ----------
    md_text : str
        The Markdown text to parse.

    Returns
    -------
    str
        The content of the first fenced code block, or an empty string if none is found.
    """
    # Initialize the Markdown parser with a custom renderer
    md_instance = marko.Markdown(renderer=MarkdownRenderer)
    md_ast = md_instance.parse(md_text)
    code_list = list()

    # Iterate through the children of the parsed Markdown AST
    # and find the first fenced code block
    for child in md_ast.children:
        child_type = child.get_type()
        if child_type == "FencedCode":
            code_list.extend(md_instance.renderer.render(child).split("\n"))
            break

    # Return the code block as a string
    return "\n".join(code_list)
