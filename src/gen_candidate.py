"""
Author       : Radon
Date         : 2025-06-24 17:28:25
LastEditors  : Radon
LastEditTime : 2025-09-02 09:10:15
Description  : MR Identification via LLM, CoT, and RAG
"""

import argparse
import concurrent.futures
import json
import math
import os
import random
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from timeout_decorator import TimeoutError, timeout

from .utils import *

# fmt:off
########## GLOBAL VARIABLES ##########
VECTOR_STORE = None     # Vector store for external corpus
ALPHA        = 1.0      # Factor of temperature
BETA         = 0.5      # Factor of top_p
EPSILON      = 0.1      # A small constant to avoid division by zero
MAX_WEIGHT   = 10.0     # Maximum weight for quadratic score calculation
GEMMA        = 8.0      # Factor of (ALPHA*temperature + BETA*top_p)^2 in quadratic score calculation
######################################
# fmt:on


def calculate_score_exp(cali_res_lst: list[tuple[Agent, bool, str]]) -> float:
    """Calculate the confidence score based on exponential decay.

    Parameters
    ----------
    cali_res_lst : list[tuple[Agent, bool, str]]
        List of tuples containing calibration agent, verification result of MR candidate, and message.

    Returns
    -------
    float
        The calculated confidence score.
    """
    mol = 0.0
    den = 0.0
    for i in range(len(cali_res_lst)):
        agent, result, _ = cali_res_lst[i]
        temp = agent.config["temperature"]
        top_p = agent.config["top_p"]
        d = ALPHA * temp + BETA * top_p
        w = math.exp(-d)
        j = 1 if result else 0
        mol += w * j
        den += w
    score = mol / den if den > 0 else -1.0
    return score


def calculate_score_lin(cali_res_lst: list[tuple[Agent, bool, str]]) -> float:
    """Calculate the confidence score using a linear? method.

    Parameters
    ----------
    cali_res_lst : list[tuple[Agent, bool, str]]
        List of tuples containing calibration agent, verification result of MR candidate, and message.

    Returns
    -------
    float
        The calculated confidence score.
    """
    mol = 0.0
    den = 0.0
    for i in range(len(cali_res_lst)):
        agent, result, _ = cali_res_lst[i]
        temp = agent.config["temperature"]
        top_p = agent.config["top_p"]
        d = ALPHA * temp + BETA * top_p
        w = 1.0 / (d + EPSILON)
        j = 1 if result else 0
        mol += w * j
        den += w
    score = mol / den if den > 0 else -1.0
    return score


def calculate_score_log(cali_res_lst: list[tuple[Agent, bool, str]]) -> float:
    """Calculate the confidence score using a logarithmic method.

    Parameters
    ----------
    cali_res_lst : list[tuple[Agent, bool, str]]
        List of tuples containing calibration agent, verification result of MR candidate, and message.

    Returns
    -------
    float
        The calculated confidence score.
    """
    mol = 0.0
    den = 0.0
    for i in range(len(cali_res_lst)):
        agent, result, _ = cali_res_lst[i]
        temp = agent.config["temperature"]
        top_p = agent.config["top_p"]
        d = ALPHA * temp + BETA * top_p
        w = 1.0 / (math.log(d + 1.0) + EPSILON)
        j = 1 if result else 0
        mol += w * j
        den += w
    score = mol / den if den > 0 else -1.0
    return score


def calculate_score_qua(cali_res_lst: list[tuple[Agent, bool, str]]) -> float:
    """Calculate the confidence score using a quadratic method.

    Parameters
    ----------
    cali_res_lst : list[tuple[Agent, bool, str]]
        List of tuples containing calibration agent, verification result of MR candidate, and message.

    Returns
    -------
    float
        The calculated confidence score.
    """
    mol = 0.0
    den = 0.0
    for i in range(len(cali_res_lst)):
        agent, result, _ = cali_res_lst[i]
        temp = agent.config["temperature"]
        top_p = agent.config["top_p"]
        d = ALPHA * temp + BETA * top_p
        w = max(0, MAX_WEIGHT - GEMMA * d**2)
        j = 1 if result else 0
        mol += w * j
        den += w
    score = mol / den if den > 0 else -1.0
    return score


def calculate_score_van(cali_res_lst: list[tuple[Agent, bool, str]]) -> float:
    """Calculate the confidence score using a vanilla method.

    Parameters
    ----------
    cali_res_lst : list[tuple[Agent, bool, str]]
        List of tuples containing calibration agent, verification result of MR candidate, and message.

    Returns
    -------
    float
        The calculated confidence score.
    """
    mol = 0
    den = 0
    for i in range(len(cali_res_lst)):
        _, result, _ = cali_res_lst[i]
        mol += 1 if result else 0
        den += 1
    score = mol / den
    return score


def calculate_score(cali_res_lst: list[tuple[Agent, bool, str]], method: str) -> float:
    """Confidence score calculation based on the specified method.

    Parameters
    ----------
    cali_res_lst : list[tuple[Agent, bool, str]]
        List of tuples containing calibration agent, verification result of MR candidate, and message.
    method : str
        The method for confidence score calculation. Options are "EXP", "LIN", "LOG, and "QUA".

    Returns
    -------
    float
        The calculated confidence score.
    """
    if method == "EXP":
        return calculate_score_exp(cali_res_lst)
    elif method == "LIN":
        return calculate_score_lin(cali_res_lst)
    elif method == "LOG":
        return calculate_score_log(cali_res_lst)
    elif method == "QUA":
        return calculate_score_qua(cali_res_lst)
    elif method == "VAN":
        return calculate_score_van(cali_res_lst)
    return -1.0  # Unlikely to reach here, but just in case


def distill(agent: Agent, index: int, cali_res_lst: list[tuple[Agent, bool, str]]) -> str:
    """Distill the error messages from calibration agents to generate a concise error message.

    Parameters
    ----------
    index : int
        User prompt index, used to select the appropriate prompt template.
    cali_res_lst : list[tuple[Agent, bool, str]]
        List of tuples containing calibration agent, verification result of MR candidate, and message.

    Returns
    -------
    str
        A distilled error message summarizing the issues found by calibration agents.
    """
    # Get error messages generated by calibration agents
    error_messages = str()
    for i in range(len(cali_res_lst)):
        _, result, message = cali_res_lst[i]
        if result:
            continue
        error_messages += f"Agent {i + 1} reported an error:\n\n{message}\n\n"
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
    code = remove_code_fences(candidate)
    Path(out_path).write_text(code, encoding="utf-8")


def main(usr_config: dict):
    """Main function to perform metamorphic relation identification using LLM, CoT, and RAG.

    Parameters
    ----------
    usr_cfg : dict
        User configuration dictionary containing model parameters and other settings.
    """
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

    # candidates store the existing metamorphic relation candidates or existing metamorphic relations
    candidates = list()
    lang = get_first_code_block(replacements["example_mr"]).split("\n")[0].strip("```").strip()
    lang = "py" if lang == "python" else lang
    if usr_config.get("existing_mrs") is not None:
        for f in usr_config["existing_mrs"]:
            mr = Path(f).read_text(encoding="utf-8")
            candidates.append(f"```{lang}\n{mr}\n```")

    # Prepare some variables for the identification process
    cnt = 0  # Counter for the number of metamorphic relation candidates identified
    gen_situ = [0, 0]  # Counter for the number of successful and failed MR generation attempts

    # Start metamorphic relation identification loop
    while cnt < max_mrs:
        SAYF("=" * 20 + f" Iteration {cnt + 1} " + "=" * 20 + "\n")

        index = 0
        gen_succ = False
        start_time_ms = get_cur_time_ms()
        out_dir = os.path.join(usr_config["output"], str(start_time_ms))

        # Initialize identification agent with existing MR candidates
        prompt_prevent_dup = str()
        if len(candidates) > 0:
            prompt_prevent_dup = "\n\n".join(candidates)
            prompt_prevent_dup = f"Please do not generate a metamorphic relation that is repeated with the following:\n{prompt_prevent_dup}\n\n"
        replacements["prompt_prevent_dup"] = prompt_prevent_dup
        # TODO: Add tools for reading code?
        agent_iden = Agent(config_iden, [retrieve], replacements)

        # Generate unique thread IDs for chating iteratively
        agent_iden.runnable_config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})
        agent_distn.runnable_config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})
        for i in range(len(agent_cali)):
            agent_cali[i].runnable_config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})

        # Start a new chat to identify one metamorphic relation candidate
        retry = 3
        while index < max_iter:
            # Prompt identification agent to generate a metamorphic relation candidate, then
            # extract metamorphic relation candidate, prompt calibration agents to verify
            # the MR candidate.
            try:
                act = "generate" if index == 0 else "fix"
                ACTF(f"Prompting identification agent to {act} a metamorphic relation candidate ...")
                response = identify(agent_iden, index, replacements)
                if len(response) == 0:
                    FATAL("Failed to generate response from identification agent!")
                candidate = get_first_code_block(response)

                # TODO: Sometime llm may not put the codified MR candidate in the code block.
                # We brute-force assign response to the candidate and surround it with a code
                # fence. This is a bad idea but I haven't thought of a better solution yet.
                if len(candidate) == 0:
                    candidate = f"```{lang}\n{response}\n```"
                ACTF("Prompting calibration agent(s) to verify the MR candidate ...")
                cali_res_lst = list()
                if usr_config["cali_linear"]:
                    cali_res_lst = calibrate_linear(agent_cali, index, replacements, candidate)
                else:
                    cali_res_lst = calibrate_parallel(agent_cali, index, replacements, candidate)

                # Calculate confidence score of calibration
                score = calculate_score(cali_res_lst, calc_method)

                # If confidence score less than threshold, collect & distill the error messages,
                # else, update existing MR candidates and open a new chat to generate a new MR candidate
                if score < score_threshold:
                    WARNF(f"Confidence score is lower than threshold ({score} < {score_threshold}), distilling error messages ...")
                    distn_err_msg = distill(agent_distn, index, cali_res_lst)
                    replacements["distn_error_messages"] = distn_err_msg
                else:
                    OKF(f"Confidence score is satisfied ({score} >= {score_threshold}), adding to candidate list ...")
                    gen_succ = True
                    break
                index += 1
            except BaseException as e:
                if retry <= 0:
                    FATAL(f"Failed to generate a metamorphic relation candidate after {retry} attempts! Error: {repr(e)}")
                retry -= 1
                t = random.randint(1, 60)  # Have a break :)
                WARNF("ERROR: " + repr(e))
                WARNF(f"Have a break for {t} seconds ... ({retry} attempts left)")
                time.sleep(t)
                continue

        # Identification is done, we can now create the output directory
        os.makedirs(usr_config["output"], exist_ok=True)
        os.mkdir(out_dir)

        # if generated successfully, append the candidate to the list and save it to the local,
        # otherwise, log the failure and continue to the next iteration
        if gen_succ:
            candidates.append(candidate)
            ext = candidate.split("\n")[0].strip("```").strip()
            ext = "py" if ext == "python" else ext
            out_path = os.path.join(out_dir, f"mr_candidate.{ext}")
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
        stats_path = os.path.join(out_dir, "iden_stats")
        write_stats(stats_path, log_dict)

        # Log chat history of identification, calibration, and distillation agents to the local
        save_agent_messages(agent_iden, os.path.join(out_dir, "agent_iden_messages.txt"))
        save_agent_messages(agent_distn, os.path.join(out_dir, "agent_distn_messages.txt"))
        for i in range(len(agent_cali)):
            save_agent_messages(agent_cali[i], os.path.join(out_dir, f"agent_cali_{i}_messages.txt"))

        cnt += 1

    OKF(f"We're done here! Identification details: {gen_situ[1]} succ, {gen_situ[0]} failed.")


def write_stats(stats_path: str, info_dict: dict):
    """Write statistics to a file.

    Parameters
    ----------
    stats_path : str
        The path to the output file where statistics will be saved.
    info_dict : dict
        Dictionary containing statistics information to be written to the file.
    """
    with open(stats_path, mode="w", encoding="utf-8") as f:
        mx_len = 0
        for k, _ in info_dict.items():
            mx_len = max(mx_len, len(k))
        for k, v in info_dict.items():
            f.write(f"{k.ljust(mx_len)}: {v}\n")


def identify(agent_iden: Agent, index: int, replacements: dict) -> str:
    """Identify a metamorphic relation candidate using the identification agent.

    Parameters
    ----------
    agent_iden : Agent
        The agent responsible for identifying metamorphic relation candidates.
    index : int
        User prompt index, used to select the appropriate prompt template.
    replacements : dict
        Dictionary of replacements for the prompt template, containing necessary context and information.

    Returns
    -------
    str
        The content responsed by the agent.
    """
    i = min(index, len(agent_iden.config["prompts"]["user"]) - 1)
    prompt_template = PromptTemplate.from_file(agent_iden.config["prompts"]["user"][i])
    usr_prompt = prompt_template.invoke(replacements).to_string()
    response = agent_iden.instance.invoke(
        {"messages": [{"role": "user", "content": usr_prompt}]},
        config=agent_iden.runnable_config,
    )
    return response["messages"][-1].content


def calibrate(agent: Agent, index: int, replacements: dict, candidate: str) -> tuple[Agent, bool, str]:
    """Calibrate the metamorphic relation candidate using a single calibration agent.

    Parameters
    ----------
    agent : Agent
        The calibration agent responsible for verifying the MR candidate.
    index : int
        User prompt index, used to select the appropriate prompt template.
    replacements : dict
        Dictionary of replacements for the prompt template, containing necessary context and information.
    candidate : str
        The metamorphic relation candidate to be verified by the calibration agent.

    Returns
    -------
    tuple[Agent, bool, str]
        A tuple containing:
        - The calibration agent that performed the verification.
        - A boolean indicating whether the MR candidate is valid (True) or invalid (False).
        - The message generated by the calibration agent during the verification process.
    """
    i = min(index, len(agent.config["prompts"]["user"]) - 1)
    prompt_template = PromptTemplate.from_file(agent.config["prompts"]["user"][i])
    usr_prompt = prompt_template.partial(**replacements).invoke({"gen_mrc": candidate}).to_string()
    response = agent.instance.invoke(
        {"messages": [{"role": "user", "content": usr_prompt}]},
        config=agent.runnable_config,
    )
    message = response["messages"][-1].content
    code_block = get_first_code_block(message)
    if "invalid" in code_block.lower():
        result = False
    else:
        result = True
    return agent, result, message


@timeout(600, timeout_exception=TimeoutError)
def calibrate_parallel(agents: list[Agent], index: int, replacements: dict, candidate: str) -> list[tuple[Agent, bool, str]]:
    """Perform calibration of the metamorphic relation candidate using multiple agents (calibrate in parallel).

    Parameters
    ----------
    agents : list[Agent]
        List of calibration agents to verify the MR candidate.
    index : int
        User prompt index, used to select the appropriate prompt template.
    replacements : dict
        Dictionary of replacements for the prompt template, containing necessary context and information.
    candidate : str
        The metamorphic relation candidate to be verified by the calibration agents.

    Returns
    -------
    list[tuple[Agent, bool, str]]
        A list of tuples, each containing:
        - The calibration agent that performed the verification.
        - A boolean indicating whether the MR candidate is valid (True) or invalid (False).
        - The message generated by the calibration agent during the verification process.
    """
    cali_res_lst = list()
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(agents)) as executor:
        futures = {executor.submit(calibrate, agent, index, replacements, candidate): agent for agent in agents}
        for future in concurrent.futures.as_completed(futures):
            cali_res = future.result()
            cali_res_lst.append(cali_res)
    return cali_res_lst


@timeout(600, timeout_exception=TimeoutError)
def calibrate_linear(agents: list[Agent], index: int, replacements: dict, candidate: str) -> list[tuple[Agent, bool, str]]:
    """Perform calibration of the metamorphic relation candidate using multiple agents (calibrate one at a time).

    Parameters
    ----------
    agents : list[Agent]
        List of calibration agents to verify the MR candidate.
    index : int
        User prompt index, used to select the appropriate prompt template.
    replacements : dict
        Dictionary of replacements for the prompt template, containing necessary context and information.
    candidate : str
        The metamorphic relation candidate to be verified by the calibration agents.

    Returns
    -------
    list[tuple[Agent, bool, str]]
        A list of tuples, each containing:
        - The calibration agent that performed the verification.
        - A boolean indicating whether the MR candidate is valid (True) or invalid (False).
        - The message generated by the calibration agent during the verification process.
    """
    cali_res_lst = list()
    for agent in agents:
        cali_res = calibrate(agent, index, replacements, candidate)
        cali_res_lst.append(cali_res)
    return cali_res_lst


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MR Identification via LLM, CoT, and RAG")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    parser.add_argument("--linear", action="store_true", help="Whether use linear calibration")
    args = parser.parse_args()
    load_dotenv()
    cfg_txt = Path(args.config).read_text(encoding="utf-8")
    usr_cfg = json.loads(os.path.expandvars(cfg_txt))
    usr_cfg["cali_linear"] = args.linear
    main(usr_cfg)
