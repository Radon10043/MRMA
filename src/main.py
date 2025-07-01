"""
Author       : Radon
Date         : 2025-06-24 17:28:25
LastEditors  : Radon
LastEditTime : 2025-07-01 17:03:56
Description  : MR Identification via LLM, CoT, and RAG
"""

import argparse
import json
import math
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from utils import *

# fmt:off
########## GLOBAL VARIABLES ##########
VECTOR_STORE = None     # Vector store for external corpus
ALPHA = 1.0             # Factor of temperature
BETA = 0.5              # Factor of top_p
EPSILON = 0.1           # A small constant to avoid division by zero
MAX_WEIGHT = 10.0       # Maximum weight for quadratic score calculation
GEMMA = 8.0             # Factor of (ALPHA*temperature + BETA*top_p)^2 in quadratic score calculation
######################################
# fmt:on


class Agent:

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
            top_p=config.get("top_p", 0.9),
        )
        prompt_template = PromptTemplate.from_file(config["prompts"]["system"])
        self.sys_prompt = prompt_template.invoke(replacements).to_string()
        memory = MemorySaver()
        self.instance = create_react_agent(
            model=self.llm,
            tools=tools,
            checkpointer=memory,
            prompt=self.sys_prompt,
        )


def calculate_score_exp(agents: list[Agent], results: list[bool]) -> float:
    """Calculate the confidence score based on exponential decay.

    Parameters
    ----------
    agents : list[Agent]
        List of agents involved in the calibration process.
    results : list[bool]
        List of boolean results from the calibration agents.

    Returns
    -------
    float
        The calculated confidence score.
    """
    mol = 0.0
    den = 0.0
    for i in range(len(agents)):
        temp = agents[i].config["temperature"]
        top_p = agents[i].config["top_p"]
        d = ALPHA * temp + BETA * top_p
        w = math.exp(-d)
        j = 1 if results[i] else 0
        mol += w * j
        den += w
    score = mol / den if den > 0 else -1.0
    return score


def calculate_score_lin(agents: list[Agent], results: list[bool]) -> float:
    """Calculate the confidence score using a linear? method.

    Parameters
    ----------
    agents : list[Agent]
        List of agents involved in the calibration process.
    results : list[bool]
        List of boolean results from the calibration agents.

    Returns
    -------
    float
        The calculated confidence score.
    """
    mol = 0.0
    den = 0.0
    for i in range(len(agents)):
        temp = agents[i].config["temperature"]
        top_p = agents[i].config["top_p"]
        d = ALPHA * temp + BETA * top_p
        w = 1.0 / (d + EPSILON)
        j = 1 if results[i] else 0
        mol += w * j
        den += w
    score = mol / den if den > 0 else -1.0
    return score


def calculate_score_log(agents: list[Agent], results: list[bool]) -> float:
    """Calculate the confidence score using a logarithmic method.

    Parameters
    ----------
    agents : list[Agent]
        List of agents involved in the calibration process.
    results : list[bool]
        List of boolean results from the calibration agents.

    Returns
    -------
    float
        The calculated confidence score.
    """
    mol = 0.0
    den = 0.0
    for i in range(len(agents)):
        temp = agents[i].config["temperature"]
        top_p = agents[i].config["top_p"]
        d = ALPHA * temp + BETA * top_p
        w = 1.0 / (math.log(d + 1.0) + EPSILON)
        j = 1 if results[i] else 0
        mol += w * j
        den += w
    score = mol / den if den > 0 else -1.0
    return score


def calculate_score_qua(agents: list[Agent], results: list[bool]) -> float:
    """Calculate the confidence score using a quadratic method.

    Parameters
    ----------
    agents : list[Agent]
        List of agents involved in the calibration process.
    results : list[bool]
        List of boolean results from the calibration agents.

    Returns
    -------
    float
        The calculated confidence score.
    """
    mol = 0.0
    den = 0.0
    for i in range(len(agents)):
        temp = agents[i].config["temperature"]
        top_p = agents[i].config["top_p"]
        d = ALPHA * temp + BETA * top_p
        w = max(0, MAX_WEIGHT - GEMMA * d**2)
        j = 1 if results[i] else 0
        mol += w * j
        den += w
    score = mol / den if den > 0 else -1.0
    return score


def calculate_score(agents: list[Agent], results: list[bool], method: str) -> float:
    """Confidence score calculation based on the specified method.

    Parameters
    ----------
    agents : list[Agent]
        List of agents involved in the calibration process.
    results : list[bool]
        List of boolean results from the calibration agents, where True indicates a valid MR candidate and False indicates an invalid one.
    method : str
        The method for confidence score calculation. Options are "EXP", "REC", etc.

    Returns
    -------
    float
        The calculated confidence score.
    """
    if method == "EXP":
        return calculate_score_exp(agents, results)
    elif method == "LIN":
        return calculate_score_lin(agents, results)
    elif method == "LOG":
        return calculate_score_log(agents, results)
    elif method == "QUA":
        return calculate_score_qua(agents, results)
    return -1.0  # Unlikely to reach here, but just in case


def distill(agent: Agent, index: int, messages: list[str], results: list[bool]) -> str:
    """Distill the error messages from calibration agents to generate a concise error message.

    Parameters
    ----------
    agent : Agent
        The agent responsible for distillation.
    index : int
        User prompt index.
    messages : list[str]
        List of error messages from calibration agents.
    results : list[bool]
        List of calibration results of calibration agents.

    Returns
    -------
    str
        A distilled error message summarizing the issues found by calibration agents.
    """
    # Get error messages generated by calibration agents
    error_messages = str()
    for i in range(len(messages)):
        if results[i]:
            continue
        error_messages += f"Agent {i + 1} reported an error:\n\n{messages[i]}\n\n"
    idx = min(index, len(agent.config["prompts"]["user"]) - 1)
    prompt_template = PromptTemplate.from_file(agent.config["prompts"]["user"][idx])
    usr_prompt = prompt_template.invoke({"error_messages": error_messages}).to_string()

    # Distill error messages
    response = agent.instance.invoke(
        {"messages": [{"role": "user", "content": usr_prompt}]},
        config=agent.runnable_config,  # Maybe iterative chat is unnecessary for distillation?
    )
    return response["messages"][-1].content


def init_vector_store(corpus_path: str):
    """Initialize the vector store with the given corpus.

    Parameters
    ----------
    corpus_path : str
        The path to the external corpus file.
    """
    # Load external corpus
    global VECTOR_STORE
    loader = TextLoader(corpus_path, encoding="utf-8")
    docs = loader.load()

    # Split document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    all_splits = text_splitter.split_documents(docs)

    # Add splits to vector store
    VECTOR_STORE = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-large"))
    VECTOR_STORE.add_documents(all_splits)


@tool(response_format="content_and_artifact")
def retrieve(query: str) -> tuple[str, list]:
    """Retrieve information related to a query.

    Parameters
    ----------
    query : str
        The query to search for relevant information.

    Returns
    -------
    tuple[str, list]
        A tuple containing a serialized string of retrieved documents and a list of Document objects.
    """
    retrived_docs = VECTOR_STORE.similarity_search(query)  # type: ignore
    serialized = "\n\n".join((f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in retrived_docs))
    return serialized, retrived_docs


def save_mr_candidate(candidate: str, out_path: str):
    """Save a metamorphic relation candidate to a file.

    Parameters
    ----------
    candidate : str
        The metamorphic relation candidate to be saved.
    out_path : str
        The path to the output file where the candidate will be saved.
    """
    with open(out_path, mode="w", encoding="utf-8") as f:
        code = candidate.split("\n")[1:-1]
        f.write("\n".join(code))


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


def main(usr_config: dict):
    """Main function to perform metamorphic relation identification using LLM, CoT, and RAG.

    Parameters
    ----------
    usr_cfg : dict
        User configuration dictionary containing model parameters and other settings.
    """
    load_dotenv()  # Load environment variables from .env file

    # Split user configs
    config_iden = usr_config["agent_iden"]
    config_cali = usr_config["agent_cali"]
    config_distn = usr_config["agent_distn"]
    replacements = usr_config["replacements"]
    calc_method = usr_config.get("confidence_calc", "EXP")
    score_threshold = usr_config.get("score_threshold", 0.6)
    max_mrs, max_iter = usr_config["max_MRs"], usr_config["max_iter"]

    # Replace placeholders in the replacements dictionary
    for key, value in replacements.items():
        if isinstance(value, str) and Path(value).exists():
            replacements[key] = Path(value).read_text(encoding="utf-8")

    # Initialize vector store
    init_vector_store(config_iden.get("external_corpus"))

    # Initialize calibration and distilliation agents.Identification agent is
    # initilized later since we need update its system prompt to prevent
    # duplicate MR candidate generation
    ACTF("Initializing agents ...")
    agent_distn = Agent(config_distn, [], replacements)
    agent_cali = list()
    for cfg in config_cali:
        agent = Agent(cfg, [], replacements)
        agent_cali.append(agent)

    # Prepare some variables for the identification process
    candidates = list()  # List to store identified metamorphic relation candidates
    cnt = 0  # Counter for the number of metamorphic relation candidates identified
    gen_situ = [0, 0]  # Counter for the number of successful and failed MR generation attempts

    # Some preprocessings ...
    os.makedirs(usr_config["output"], exist_ok=True)

    # Start metamorphic relation identification loop
    while cnt < max_mrs:
        SAYF("=" * 20 + f" Iteration {cnt + 1} " + "=" * 20 + "\n")

        index = 0
        gen_succ = False
        start_time_ms = get_cur_time_ms()
        out_dir = os.path.join(usr_config["output"], str(start_time_ms))
        os.mkdir(out_dir)

        # Initialize identification agent with existing MR candidates
        prompt_prevent_dup = str()
        if len(candidates) > 0:
            prompt_prevent_dup = "\n\n".join(candidates)
            prompt_prevent_dup = f"Please do not generate a metamorphic relation that is repeated with the following:\n{prompt_prevent_dup}\n\n"
        replacements["prompt_prevent_dup"] = prompt_prevent_dup
        agent_iden = Agent(config_iden, [retrieve], replacements)

        # Generate unique thread IDs for chating iteratively
        agent_iden.runnable_config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})
        agent_distn.runnable_config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})
        for i in range(len(agent_cali)):
            agent_cali[i].runnable_config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})

        # Start a new chat to identify one metamorphic relation candidate
        while index < max_iter:
            # Prompt identification agent to generate a metamorphic relation candidate
            ACTF("Prompting identification agent to generate/fix a metamorphic relation candidate ...")
            i = min(index, len(agent_iden.config["prompts"]["user"]) - 1)
            prompt_template = PromptTemplate.from_file(agent_iden.config["prompts"]["user"][i])
            usr_prompt = prompt_template.invoke(replacements).to_string()
            response = agent_iden.instance.invoke(
                {"messages": [{"role": "user", "content": usr_prompt}]},
                config=agent_iden.runnable_config,
            )

            # Extract metamorphic relation candidate
            candidate = get_first_code_block(response["messages"][-1].content)

            # Prompt calibration agents to verify the MR candidate
            # TODO: It can be executed in parallel
            ACTF("Prompting calibration agent(s) to verify the MR candidate ...")
            cali_res_lst = list()
            cali_msg_lst = list()
            for agent in agent_cali:
                i = min(index, len(agent.config["prompts"]["user"]) - 1)
                prompt_template = PromptTemplate.from_file(agent.config["prompts"]["user"][i])
                usr_prompt = prompt_template.partial(**replacements).invoke({"gen_mrc": candidate}).to_string()
                response = agent.instance.invoke(
                    {"messages": [{"role": "user", "content": usr_prompt}]},
                    config=agent.runnable_config,
                )
                cali_msg = response["messages"][-1].content
                cali_res = get_first_code_block(cali_msg)
                cali_msg_lst.append(cali_msg)
                if "invalid" in cali_res.lower():
                    cali_res_lst.append(False)
                else:
                    cali_res_lst.append(True)

            # Calculate confidence score of calibration
            score = calculate_score(agent_cali, cali_res_lst, calc_method)

            # If confidence score less than threshold, collect & distill the error messages,
            # else, update existing MR candidates and open a new chat to generate a new MR candidate
            if score < score_threshold:
                WARNF(f"Confidence score is lower than threshold ({score} < {score_threshold}), distilling error messages ...")
                distn_err_msg = distill(agent_distn, index, cali_msg_lst, cali_res_lst)
                replacements["distn_error_messages"] = distn_err_msg
            else:
                OKF(f"Confidence score is satisfied ({score} >= {score_threshold}), adding to candidate list ...")
                gen_succ = True
                break
            index += 1

        # if generated successfully, append the candidate to the list and save it to the local,
        # otherwise, log the failure and continue to the next iteration
        if gen_succ:
            candidates.append(candidate)
            lang = candidate.split("\n")[0].strip("```").strip()
            out_path = os.path.join(out_dir, f"mr_candidate.{lang}")
            save_mr_candidate(candidate, out_path)
            gen_situ[1] += 1
            OKF(f"Successfully generated a valid MR candidate after {index + 1} iterations!")
        else:
            gen_situ[0] += 1
            BADF(f"Oops, failed to generate a valid MR candidate after {max_iter} iterations!")

        # Log the details of the MR candidate generation
        end_time = get_cur_time_ms()
        log_dict = {
            "result": "success" if gen_succ else "failed",
            "agent iden": agent_iden.config["model"],
            "agent iden temperature": agent_iden.config["temperature"],
            "agent iden top_p": agent_iden.config["top_p"],
            "agent distn": agent_distn.config["model"],
            "agent distn temperature": agent_distn.config["temperature"],
            "agent distn top_p": agent_distn.config["top_p"],
        }
        for i in range(len(agent_cali)):
            log_dict[f"agent cali {i + 1}"] = agent_cali[i].config["model"]
            log_dict[f"agent cali {i + 1} temperature"] = agent_cali[i].config["temperature"]
            log_dict[f"agent cali {i + 1} top_p"] = agent_cali[i].config["top_p"]
        log_dict["iteration"] = index + 1
        log_dict["start time"] = start_time_ms
        log_dict["end time"] = end_time
        log_dict["output dir"] = out_dir
        with open(os.path.join(out_dir, "iden_status"), mode="w", encoding="utf-8") as f:
            mx_len = 0
            for k, _ in log_dict.items():
                mx_len = max(mx_len, len(k))
            for k, v in log_dict.items():
                f.write(f"{k.ljust(mx_len)}: {v}\n")

        # Log chat history of identification, calibration, and distillation agents to the local
        save_agent_messages(agent_iden, os.path.join(out_dir, "agent_iden_messages.txt"))
        save_agent_messages(agent_distn, os.path.join(out_dir, "agent_distn_messages.txt"))
        for i in range(len(agent_cali)):
            save_agent_messages(agent_cali[i], os.path.join(out_dir, f"agent_cali_{i}_messages.txt"))

        cnt += 1

    OKF(f"We're done here! Identification details: {gen_situ[1]} succ, {gen_situ[0]} failed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MR Identification via LLM, CoT, and RAG")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    args = parser.parse_args()
    usr_cfg = dict()
    with open(args.config, "r", encoding="utf-8") as f:
        usr_cfg = json.load(f)
    main(usr_cfg)
