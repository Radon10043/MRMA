"""
Author       : Radon
Date         : 2025-07-21 16:32:31
LastEditors  : Radon
LastEditTime : 2025-07-21 17:54:14
Description  : Test script
"""
import itertools
import os
import random

from dotenv import load_dotenv

from src.gen_candidate import calculate_score
from src.utils import *


def test_calculate_score():
    """Test the calculate_score function with various configurations and permutations of agents."""
    load_dotenv()
    project_path = str(os.getenv("PROJECT"))
    cfg_template = {
        "model": "fake",
        "temperature": 0.5,
        "top_p": 0.5,
        "prompts": {
            "system": os.path.join(project_path, "data", "prompts", "cali", "system.md"),
            "user": [
                os.path.join(project_path, "data", "prompts", "cali", "user1.md"),
                os.path.join(project_path, "data", "prompts", "cali", "user2.md"),
            ],
        },
    }
    replacements = {
        "sut_name": "Binary Search Algorithm",
        "specification": os.path.join(project_path, "data", "specs", "Bsearch2.md"),
        "example_mr": os.path.join(project_path, "data", "example-MRs", "Bsearch2.md"),
        "example_analysis": os.path.join(project_path, "data", "example-analysis", "Bsearch2.md"),
    }

    agents = list[Agent]()
    params = [(0.25, 0.2), (0.5, 0.4), (0.75, 0.6), (1.0, 0.8)]
    for param in params:
        cfg = cfg_template.copy()
        cfg["temperature"] = param[0]
        cfg["top_p"] = param[1]
        agents.append(Agent(cfg, [], replacements))
    perms = itertools.product([True, False], repeat=len(agents))

    for perm in perms:
        cases = list[tuple]()
        for i in range(len(agents)):
            cases.append((agents[i], perm[i], ""))
        for method in ["EXP", "LOG", "LIN", "QUA", "VAN"]:
            score = calculate_score(cases, method)
            SAYF(f"perm={perm}, method={method}, score={score}\n")
        SAYF("=" * 60 + "\n")


if __name__ == "__main__":
    test_calculate_score()
