"""
Author       : Radon
Date         : 2025-06-27 16:42:43
LastEditors  : Radon
LastEditTime : 2025-09-16 19:46:13
Description  : Utility functions
"""

import os
import time
from copy import deepcopy
from typing import Tuple

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


#########################################################
### Dictionary to map sut abbreviations to full names ###
#########################################################
# fmt:off
SUT_DICT = {
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


#######################
### Config template ###
#######################
CFGTMPL_CLOSE_GROUP = {
    "agent_iden": {
        "model": "gemini-2.5-pro",
        "temperature": 1.0,
        "top_p": 1.0,
        "external_corpus": "DO NOT EDIT HERE",
        "prompts": {"system": "DO NOT EDIT HERE", "user": []},
    },
    "agent_distn": {
        "model": "gemini-2.5-flash",
        "temperature": 1.0,
        "top_p": 1.0,
        "prompts": {"system": "DO NOT EDIT HERE", "user": []},
    },
    "agent_cali": [
        {"model": "o3-2025-04-16", "temperature": 0.25, "top_p": 0.2, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
        {"model": "chatgpt-4o-latest", "temperature": 0.5, "top_p": 0.4, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
        {"model": "grok-3", "temperature": 0.75, "top_p": 0.6, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
        {"model": "claude-sonnet-4-20250514-thinking", "temperature": 1.0, "top_p": 0.8, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
    ],
    "replacements": {"sut_name": "DO NOT EDIT HERE", "specification": "DO NOT EDIT HERE", "example_mr": "DO NOT EDIT HERE", "example_analysis": "DO NOT EDIT HERE"},
    "existing_mrs": [],
    "score_calc": "EXP",
    "score_threshold": 0.6,
    "max_MRs": 10,
    "max_iter": 10,
    "output": "DO NOT EDIT HERE",
}

CFGTMPL_OPEN_GROUP = {
    "agent_iden": {
        "model": "qwen3-235b-a22b-instruct-2507",
        "temperature": 1.0,
        "top_p": 1.0,
        "external_corpus": "DO NOT EDIT HERE",
        "prompts": {"system": "DO NOT EDIT HERE", "user": []},
    },
    "agent_distn": {
        "model": "glm-4.5-air",
        "temperature": 1.0,
        "top_p": 1.0,
        "prompts": {"system": "DO NOT EDIT HERE", "user": []},
    },
    "agent_cali": [
        {"model": "glm-4.5", "temperature": 0.25, "top_p": 0.2, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
        {"model": "kimi-k2-0711-preview", "temperature": 0.5, "top_p": 0.4, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
        {"model": "deepseek-reasoner", "temperature": 0.75, "top_p": 0.6, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
        {"model": "hunyuan-large", "temperature": 1.0, "top_p": 0.8, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
    ],
    "replacements": {"sut_name": "DO NOT EDIT HERE", "specification": "DO NOT EDIT HERE", "example_mr": "DO NOT EDIT HERE", "example_analysis": "DO NOT EDIT HERE"},
    "existing_mrs": [],
    "score_calc": "EXP",
    "score_threshold": 0.6,
    "max_MRs": 10,
    "max_iter": 10,
    "output": "DO NOT EDIT HERE",
}

CFGTMPL_HYBRID_GROUP = {
    "agent_iden": {
        "model": "gemini-2.5-pro",
        "temperature": 1.0,
        "top_p": 1.0,
        "external_corpus": "DO NOT EDIT HERE",
        "prompts": {"system": "DO NOT EDIT HERE", "user": []},
    },
    "agent_distn": {
        "model": "kimi-k2-0711-preview",
        "temperature": 1.0,
        "top_p": 1.0,
        "prompts": {"system": "DO NOT EDIT HERE", "user": []},
    },
    "agent_cali": [
        {"model": "o3", "temperature": 0.25, "top_p": 0.2, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
        {"model": "qwen3-235b-a22b-instruct-2507", "temperature": 0.5, "top_p": 0.4, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
        {"model": "glm-4.5", "temperature": 0.75, "top_p": 0.6, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
        {"model": "grok-3", "temperature": 1.0, "top_p": 0.8, "prompts": {"system": "DO NOT EDIT HERE", "user": []}},
    ],
    "replacements": {"sut_name": "DO NOT EDIT HERE", "specification": "DO NOT EDIT HERE", "example_mr": "DO NOT EDIT HERE", "example_analysis": "DO NOT EDIT HERE"},
    "existing_mrs": [],
    "score_calc": "EXP",
    "score_threshold": 0.6,
    "max_MRs": 10,
    "max_iter": 10,
    "output": "DO NOT EDIT HERE",
}

CFGTMPL_SINGLE_LLM = {
    "agent_iden": {
        "model": "DO NOT EDIT HERE",
        "temperature": 1.0,
        "top_p": 1.0,
        "external_corpus": "DO NOT EDIT HERE",
        "prompts": {"system": "DO NOT EDIT HERE", "user": []},
    },
    "agent_distn": {},
    "agent_cali": [],
    "replacements": {"sut_name": "DO NOT EDIT HERE", "specification": "DO NOT EDIT HERE", "example_mr": "DO NOT EDIT HERE", "example_analysis": "DO NOT EDIT HERE"},
    "existing_mrs": [],
    "score_calc": "EXP",
    "score_threshold": 0.6,
    "max_MRs": 10,
    "max_iter": 10,
    "output": "DO NOT EDIT HERE",
}

########################
### Supported models ###
########################
SUPPORTED_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "o3-2025-04-16",
    "chatgpt-4o-latest",
    "grok-3",
    "claude-sonnet-4-20250514-thinking",
    "qwen3-235b-a22b-instruct-2507",
    "glm-4.5-air",
    "glm-4.5",
    "kimi-k2-0711-preview",
    "deepseek-reasoner",
    "hunyuan-large",
]

########################################
### Models that do not support tools ###
########################################
TOOLS_UNSUPPORTED_MODELS = {
    "chatgpt-4o-latest",
}

#######################################################################
### Model prefix and corresponding base_url and api_key envvar name ###
#######################################################################
# fmt:off
MODEL_PREFIX_ENVVAR_DICT = {
    "gemini"    : ("GOOGLE_OPENAI_API_BASE",    "GOOGLE_API_KEY"),
    "chatgpt"   : ("OPENAI_API_BASE",           "OPENAI_API_KEY"),
    "grok"      : ("XAI_OPENAI_API_BASE",       "XAI_API_KEY"),
    "claude"    : ("ANTHROPIC_OPENAI_API_BASE", "ANTHROPIC_API_KEY"),
    "qwen"      : ("ALIYUN_OPENAI_API_BASE",    "ALIYUN_API_KEY"),
    "glm"       : ("ZAI_OPENAI_API_BASE",       "ZAI_API_KEY"),
    "kimi"      : ("MOONSHOT_OPENAI_API_BASE",  "MOONSHOT_API_KEY"),
    "deepseek"  : ("DEEPSEEK_OPENAI_API_BASE",  "DEEPSEEK_API_KEY"),
    "hunyuan"   : ("HUNYUAN_OPENAI_API_BASE",   "HUNYUAN_API_KEY"),
    # FIXME: Looks fishy, but I don't have a better idea to match models like o3, o4, etc.
    "o"         : ("OPENAI_API_BASE",           "OPENAI_API_KEY"),
}
# fmt:on


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


def get_baseurl_apikey(model: str) -> Tuple[str, str]:
    """Get the base URL and API key for a given model

    Parameters
    ----------
    model : str
        The name of the model.

    Returns
    -------
    Tuple[str, str]
        The tuple of base URL and API key.
    """
    base_url, api_key = str(), str()
    for k, v in MODEL_PREFIX_ENVVAR_DICT.items():
        if model.startswith(k):
            base_url = str(os.getenv(v[0]))
            api_key = str(os.getenv(v[1]))
            break
    return base_url, api_key


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


def default_close_config(sut: str) -> dict:
    """Get the default configuration for a close group experiment.

    Parameters
    ----------
    sut : str
        The name of the software under test.

    Returns
    -------
    dict
        The default configuration dictionary.
    """
    project_path = str(os.getenv("PROJECT"))
    cfg = deepcopy(CFGTMPL_CLOSE_GROUP)
    cfg["agent_iden"]["external_corpus"] = os.path.join(project_path, "data", "corpus", sut + ".md")
    cfg["agent_iden"]["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "iden", "system.md")
    cfg["agent_iden"]["prompts"]["user"] = [
        os.path.join(project_path, "data", "prompts", "iden", "user1.md"),
        os.path.join(project_path, "data", "prompts", "iden", "user2.md"),
    ]
    cfg["agent_iden"]["base_url"], cfg["agent_iden"]["api_key"] = get_baseurl_apikey(cfg["agent_iden"]["model"])
    cfg["agent_distn"]["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "distn", "system.md")
    cfg["agent_distn"]["prompts"]["user"] = [
        os.path.join(project_path, "data", "prompts", "distn", "user1.md"),
    ]
    cfg["agent_distn"]["base_url"], cfg["agent_distn"]["api_key"] = get_baseurl_apikey(cfg["agent_distn"]["model"])
    for dt in cfg["agent_cali"]:
        dt["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "cali", "system.md")
        dt["prompts"]["user"] = [
            os.path.join(project_path, "data", "prompts", "cali", "user1.md"),
            os.path.join(project_path, "data", "prompts", "cali", "user2.md"),
        ]
        dt["base_url"], dt["api_key"] = get_baseurl_apikey(dt["model"])
    cfg["replacements"]["sut_name"] = SUT_DICT[sut]
    cfg["replacements"]["specification"] = os.path.join(project_path, "data", "specs", sut + ".md")
    cfg["replacements"]["example_mr"] = os.path.join(project_path, "data", "example-MRs", sut + ".md")
    cfg["replacements"]["example_analysis"] = os.path.join(project_path, "data", "example-analysis", sut + ".md")
    cfg["output"] = os.path.join(project_path, "workdir", "default", sut)
    cfg["existing_mrs"] = list()
    return cfg


def default_open_config(sut: str) -> dict:
    """Get the default configuration for a open group experiment.

    Parameters
    ----------
    sut : str
        The name of the software under test.

    Returns
    -------
    dict
        The default configuration dictionary.
    """
    project_path = str(os.getenv("PROJECT"))
    cfg = deepcopy(CFGTMPL_OPEN_GROUP)
    cfg["agent_iden"]["external_corpus"] = os.path.join(project_path, "data", "corpus", sut + ".md")
    cfg["agent_iden"]["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "iden", "system.md")
    cfg["agent_iden"]["prompts"]["user"] = [
        os.path.join(project_path, "data", "prompts", "iden", "user1.md"),
        os.path.join(project_path, "data", "prompts", "iden", "user2.md"),
    ]
    cfg["agent_iden"]["base_url"], cfg["agent_iden"]["api_key"] = get_baseurl_apikey(cfg["agent_iden"]["model"])
    cfg["agent_distn"]["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "distn", "system.md")
    cfg["agent_distn"]["prompts"]["user"] = [
        os.path.join(project_path, "data", "prompts", "distn", "user1.md"),
    ]
    cfg["agent_distn"]["base_url"], cfg["agent_distn"]["api_key"] = get_baseurl_apikey(cfg["agent_distn"]["model"])
    for dt in cfg["agent_cali"]:
        dt["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "cali", "system.md")
        dt["prompts"]["user"] = [
            os.path.join(project_path, "data", "prompts", "cali", "user1.md"),
            os.path.join(project_path, "data", "prompts", "cali", "user2.md"),
        ]
        dt["base_url"], dt["api_key"] = get_baseurl_apikey(dt["model"])
    cfg["replacements"]["sut_name"] = SUT_DICT[sut]
    cfg["replacements"]["specification"] = os.path.join(project_path, "data", "specs", sut + ".md")
    cfg["replacements"]["example_mr"] = os.path.join(project_path, "data", "example-MRs", sut + ".md")
    cfg["replacements"]["example_analysis"] = os.path.join(project_path, "data", "example-analysis", sut + ".md")
    cfg["output"] = os.path.join(project_path, "workdir", "default", sut)
    cfg["existing_mrs"] = list()
    return cfg


def default_hybrid_config(sut: str) -> dict:
    """Get the default configuration for a hybrid group experiment.

    Parameters
    ----------
    sut : str
        The name of the software under test.

    Returns
    -------
    dict
        The default configuration dictionary.
    """
    project_path = str(os.getenv("PROJECT"))
    cfg = deepcopy(CFGTMPL_HYBRID_GROUP)
    cfg["agent_iden"]["external_corpus"] = os.path.join(project_path, "data", "corpus", sut + ".md")
    cfg["agent_iden"]["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "iden", "system.md")
    cfg["agent_iden"]["prompts"]["user"] = [
        os.path.join(project_path, "data", "prompts", "iden", "user1.md"),
        os.path.join(project_path, "data", "prompts", "iden", "user2.md"),
    ]
    cfg["agent_iden"]["base_url"], cfg["agent_iden"]["api_key"] = get_baseurl_apikey(cfg["agent_iden"]["model"])
    cfg["agent_distn"]["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "distn", "system.md")
    cfg["agent_distn"]["prompts"]["user"] = [
        os.path.join(project_path, "data", "prompts", "distn", "user1.md"),
    ]
    cfg["agent_distn"]["base_url"], cfg["agent_distn"]["api_key"] = get_baseurl_apikey(cfg["agent_distn"]["model"])
    for dt in cfg["agent_cali"]:
        dt["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "cali", "system.md")
        dt["prompts"]["user"] = [
            os.path.join(project_path, "data", "prompts", "cali", "user1.md"),
            os.path.join(project_path, "data", "prompts", "cali", "user2.md"),
        ]
        dt["base_url"], dt["api_key"] = get_baseurl_apikey(dt["model"])
    cfg["replacements"]["sut_name"] = SUT_DICT[sut]
    cfg["replacements"]["specification"] = os.path.join(project_path, "data", "specs", sut + ".md")
    cfg["replacements"]["example_mr"] = os.path.join(project_path, "data", "example-MRs", sut + ".md")
    cfg["replacements"]["example_analysis"] = os.path.join(project_path, "data", "example-analysis", sut + ".md")
    cfg["output"] = os.path.join(project_path, "workdir", "default", sut)
    cfg["existing_mrs"] = list()
    return cfg


def default_single_config(sut: str, model: str) -> dict:
    """Get the default configuration for identification experiment via single LLM.

    Parameters
    ----------
    sut : str
        The name of the software under test.
    model : str
        The name of the LLM to be used.

    Returns
    -------
    dict
        The default configuration dictionary.
    """
    project_path = str(os.getenv("PROJECT"))
    cfg = deepcopy(CFGTMPL_SINGLE_LLM)
    cfg["agent_iden"]["external_corpus"] = os.path.join(project_path, "data", "corpus", sut + ".md")
    cfg["agent_iden"]["prompts"]["system"] = os.path.join(project_path, "data", "prompts", "iden", "system.md")
    cfg["agent_iden"]["prompts"]["user"] = [
        os.path.join(project_path, "data", "prompts", "iden", "user1.md"),
        os.path.join(project_path, "data", "prompts", "iden", "user2.md"),
    ]
    cfg["agent_iden"]["model"] = model
    cfg["agent_iden"]["base_url"], cfg["agent_iden"]["api_key"] = get_baseurl_apikey(model)
    cfg["replacements"]["sut_name"] = SUT_DICT[sut]
    cfg["replacements"]["specification"] = os.path.join(project_path, "data", "specs", sut + ".md")
    cfg["replacements"]["example_mr"] = os.path.join(project_path, "data", "example-MRs", sut + ".md")
    cfg["replacements"]["example_analysis"] = os.path.join(project_path, "data", "example-analysis", sut + ".md")
    cfg["output"] = os.path.join(project_path, "workdir", "default", sut)
    cfg["existing_mrs"] = list()
    return cfg
