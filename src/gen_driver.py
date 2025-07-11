"""
Author       : Radon
Date         : 2025-07-10 17:43:16
LastEditors  : Radon
LastEditTime : 2025-07-11 16:53:05
Description  : Generate test driver for encoded-MRCs
"""

import argparse
import json
import os
import subprocess
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig

from utils import *


def update_code(code: str, config: dict) -> str:
    """Update the code through configuration, such as adding a prefix.

    Parameters
    ----------
    code : str
        Code to be updated.
    config : dict
        Configuration dictionary.

    Returns
    -------
    str
        Updated code.
    """
    prefix = config.get("prefix", "")
    code = prefix + "\n" + code
    return code


def build_cpp(code: str) -> tuple[bool, str]:
    """Build a C++ test driver from the provided code.

    Parameters
    ----------
    code : str
        The C++ code to be compiled as a test driver.

    Returns
    -------
    tuple[bool, str]
        A tuple containing a boolean indicating success or failure, and a string with error messages if any.
    """
    cxx = "g++"
    filepath = "/tmp/test_driver.cpp"
    gtest_dir = os.getenv("GTEST_DIR")
    Path(filepath).write_text(code, encoding="utf-8")

    cmd = [
        cxx,
        filepath,
        "-std=c++17",
        "-pthread",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-o",
        "/tmp/test_driver",
        "-isystem",
        f"{gtest_dir}/googletest/include",
        f"{gtest_dir}/build/lib/libgtest.a",
        f"{gtest_dir}/build/lib/libgtest_main.a",
    ]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return result.returncode == 0, result.stderr


def main(user_config: dict):
    """Generate a test driver based on the provided user configuration.

    Parameters
    ----------
    user_config : dict
        A dictionary containing user configuration, including the agent configuration,
        candidate file path, build settings, etc.
    """
    ACTF("Initializing driver generation agent ...")
    replacements = user_config.get("replacements", {})
    config_agent = user_config["agent"]
    agent = Agent(config=config_agent, tools=[], replacements=replacements)

    # Generate unique thread ID for chating iteratively
    agent.runnable_config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})

    cand_path = user_config["candidate"]
    ext = Path(cand_path).suffix[1:]  # Remove the leading dot from the file extension
    code = Path(cand_path).read_text(encoding="utf-8")
    code = update_code(code, user_config["build"])
    code = f"```{ext}\n{code}\n```"  # Wrap code in fenced code block with language tag
    replacements["candidate"] = code

    index = 0
    max_iter = user_config.get("max_iter", 10)
    usr_pts = config_agent["prompts"]["user"]
    gen_succ = False
    compl_code = str()

    # Dictionary to hold build functions for different languages
    build_dict = {
        "cpp": build_cpp,
    }

    # Start prompting the agent to generate complete code
    while index < max_iter and not gen_succ:
        ACTF(f"Prompting agent to generate test driver code, iteration {index + 1} ...")
        i = min(index, len(usr_pts) - 1)  # Use the last prompt if index exceeds available prompts
        pt = PromptTemplate.from_file(usr_pts[i])
        prompt = pt.invoke(replacements).to_string()
        response = agent.instance.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=agent.runnable_config,
        )
        compl_code = get_first_code_block(response["messages"][-1].content)
        compl_code = compl_code.removeprefix(f"```{ext}\n").rstrip("`\n")
        gen_succ, error_messages = build_dict[ext](compl_code)
        replacements["error_messages"] = error_messages
        index += 1
        if not gen_succ:
            WARNF("Failed to build the generated test driver, retrying ...")

    out_dir = os.path.dirname(cand_path)
    if gen_succ:
        # Save the completed code to the same directory as the candidate file
        out_path = os.path.join(out_dir, "test_driver." + ext)
        Path(out_path).write_text(compl_code, encoding="utf-8")
        OKF(f"Test driver generated successfully after {index} iterations, check it at: {out_path}")
    else:
        BADF(f"Failed to generate a valid test driver after {max_iter} iterations.")

    # Save the agent's messages to a file
    save_agent_messages(agent, os.path.join(out_dir, "agent_test_messages.txt"))

    OKF("We're done here!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test driver for encoded-MRCs")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    args = parser.parse_args()
    load_dotenv()
    cfg_text = Path(args.config).read_text(encoding="utf-8")
    usr_cfg = json.loads(os.path.expandvars(cfg_text))
    main(usr_cfg)
