"""
Author       : Radon
Date         : 2025-06-27 16:42:43
LastEditors  : Radon
LastEditTime : 2025-07-23 14:14:53
Description  : Utility functions
"""

import os
import time

import marko
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
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
    SAYF(TerminalColors.cLRD + "[-] PROGRAM ABORT : " + TerminalColors.cRST + msg + "\n")
    exit(1)


def PFATAL(msg: str):
    SAYF(TerminalColors.cLRD + "\n[-] SYSTEM ERROR : " + TerminalColors.cBRI + msg + TerminalColors.cRST + "\n")
    exit(1)


class Agent:
    """Agent class for managing a chat model and tools."""

    def __init__(self, config: dict, tools: list, replacements: dict = {}):
        """Initialize an agent with a chat model and tools.

        Parameters
        ----------
        config : dict
            Configuration dictionary.
        tools : list
            List of tools to be used by the agent.
        replacements : dict, optional
            Dictionary of replacements for the prompt template, by default an empty dict
        """
        self.config = config
        self.runnable_config = RunnableConfig({"configurable": {"thread_id": "foo"}})  # Placeholder for thread ID
        self.llm = init_chat_model(
            model=config.get("model"),
            temperature=config.get("temperature", 1.0),
            model_provider="openai",
            top_p=config.get("top_p", 1.0),
            base_url=config.get("base_url", os.getenv("OPENAI_API_BASE")),
            api_key=config.get("api_key", os.getenv("OPENAI_API_KEY")),
        )
        prompt_template = PromptTemplate.from_file(config["prompts"]["system"])
        self.sys_prompt = prompt_template.invoke(replacements).to_string()
        if len(tools) > 0:
            self.sys_prompt += f"\n\nYou can access the following tools:\n\n{[tool.name for tool in tools]}\n\n"
        memory = MemorySaver()
        self.instance = create_react_agent(
            model=self.llm,
            tools=tools,
            checkpointer=memory,
            prompt=self.sys_prompt,
        )


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


def get_cur_time_ms() -> int:
    """Get the current timestamp in milliseconds.

    Returns
    -------
    int
        The current timestamp in milliseconds.
    """
    now = time.time_ns()
    ms = now // 1_000_000
    return ms


def save_agent_messages(agent: Agent, out_path: str):
    """Save the chat history of an agent to a file.

    Parameters
    ----------
    agent : Agent
        The agent whose chat history is to be saved.
    out_path : str
        The path to the output file where the chat history will be saved.
    """
    state = agent.instance.get_state(config=agent.runnable_config).values
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(" System Prompt ".center(81, "=") + f"\n\n{agent.sys_prompt}\n\n")
        if not "messages" in state:
            return
        for message in state["messages"]:
            f.write(message.pretty_repr() + "\n")


def remove_code_fences(code: str) -> str:
    """Remove code fences from a string.

    Parameters
    ----------
    code : str
        The string containing code with fences.

    Returns
    -------
    str
        The string with code fences removed.
    """
    code_lst = code.split("\n")
    s, e = 0, len(code_lst) - 1
    while s < len(code_lst) and not code_lst[s].startswith("```"):
        s += 1
    while e >= 0 and not code_lst[e].startswith("```"):
        e -= 1
    return "\n".join(code_lst[s + 1 : e]).strip() if s < e else code