"""
Author       : Radon
Date         : 2025-07-10 17:43:16
LastEditors  : Radon
LastEditTime : 2025-07-10 22:12:57
Description  : Generate test driver for encoded-MRCs
"""

import argparse
import json
import os
import uuid
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig

from utils import *


def build_cpp(code: str, config: dict) -> tuple[bool, str]:
    cxx = "g++"
    prefix = config.get("prefix", "")
    code = prefix + "\n" + code
    filepath = "/tmp/test_driver.cpp"
    Path(filepath).write_text(code, encoding="utf-8")

    cmd = [
        cxx,
        filepath,
        "-std=c++17",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-o",
        "test_driver",
        "-isystem",
        "/home/tools/googletest-1.14.0/googletest/include",
        "/home/tools/googletest-1.14.0/lib/libgtest.a",
        "/home/tools/googletest-1.14.0/lib/libgtest_main.a",
    ]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return result.returncode == 0, result.stderr


def main(user_config: dict):
    load_dotenv()  # Load environment variables from .env file

    replacements = user_config.get("replacements", {})
    config_agent = user_config["agent"]
    agent = Agent(config=config_agent, tools=[], replacements=replacements)

    # Generate unique thread ID for chating iteratively
    agent.runnable_config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})

    cand_path = user_config["candidate"]
    ext = Path(cand_path).suffix[1:]  # Remove the leading dot from the file extension
    code = Path(cand_path).read_text(encoding="utf-8")
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
        i = min(index, max_iter)
        pt = PromptTemplate.from_file(usr_pts[i])
        prompt = pt.invoke(replacements).to_string()
        response = agent.instance.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=agent.runnable_config,
        )
        compl_code = get_first_code_block(response["messages"][-1].content)
        compl_code = compl_code.removeprefix(f"```{ext}\n").removesuffix("```")
        gen_succ, error_messages = build_dict[ext](compl_code, user_config["build"])
        replacements["error_messages"] = error_messages
        index += 1

    out_dir = os.path.dirname(cand_path)
    if gen_succ:
        # Save the completed code to the same directory as the candidate file
        out_path = os.path.join(out_dir, "test_driver." + ext)
        Path(out_path).write_text(compl_code, encoding="utf-8")
        OKF("Test driver generated successfully, check it at: " + out_path)
    else:
        BADF(f"Failed to generate a valid test driver after {max_iter} iterations.")

    # Save the agent's messages to a file
    save_agent_messages(agent, os.path.join(out_dir, "agent_test_messages.txt"))

    OKF("We're done here!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test driver for encoded-MRCs")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    args = parser.parse_args()
    cfg_text = Path(args.config).read_text(encoding="utf-8")
    usr_cfg = json.loads(os.path.expandvars(cfg_text))
    main(usr_cfg)
