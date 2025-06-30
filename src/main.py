"""
Author       : Radon
Date         : 2025-06-24 17:28:25
LastEditors  : Radon
LastEditTime : 2025-06-30 20:09:44
Description  : MR Identification via LLM, CoT, and RAG
"""

import argparse
import json
import math
import uuid
from pathlib import Path

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

########## GLOBAL VARIABLES ##########
VECTOR_STORE = None
ALPHA = 0.8
BETA = 0.4
EPSILON = 0.1
######################################


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
        self.llm = init_chat_model(
            model=config.get("model"),
            temperature=config.get("temperature", 1.0),
            model_provider="openai",
            top_p=config.get("top_p", 0.9),
        )
        prompt_template = PromptTemplate.from_file(config["prompts"]["system"])
        sys_prompt = prompt_template.invoke(replacements).to_string()
        memory = MemorySaver()
        self.instance = create_react_agent(
            model=self.llm,
            tools=tools,
            checkpointer=memory,
            prompt=sys_prompt,
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
        w = math.exp(-ALPHA * temp - BETA * top_p)
        j = 1 if results[i] else 0
        mol += w * j
        den += w
    score = mol / den if den > 0 else -1.0
    return score


def calculate_score_rec(agents: list[Agent], results: list[bool]) -> float:
    # TODO: Implement the recursive confidence score calculation
    return 0.0


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
    elif method == "REC":
        return calculate_score_rec(agents, results)
    return -1.0  # Unlikely to reach here, but just in case


def distillation():
    # TODO: Implement the distillation process
    pass


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
    max_mrs, max_iter = usr_config["max_MRs"], usr_config["max_iter"]

    # Replace placeholders in the replacements dictionary
    for key, value in replacements.items():
        if isinstance(value, str) and Path(value).exists():
            replacements[key] = Path(value).read_text(encoding="utf-8")

    # Initialize vector store
    init_vector_store(config_iden.get("external_corpus"))

    # Initialize identification, calibration, and distilliation agents
    agent_iden = Agent(config_iden, [retrieve], replacements)
    agent_distn = Agent(config_distn, [], replacements)
    agent_cali = list()
    for cfg in config_cali:
        agent = Agent(cfg, [], replacements)
        agent_cali.append(agent)

    # Start metamorphic relation identification loop
    cnt = 0
    while cnt < max_mrs:
        index = 0

        # Generate unique thread IDs for chating iteratively
        thread_id_dict = dict()
        thread_id_dict["iden"] = uuid.uuid4().hex
        thread_id_dict["distn"] = uuid.uuid4().hex
        thread_id_dict["cali"] = [uuid.uuid4().hex for _ in range(len(agent_cali))]

        # Start a new chat to identify one metamorphic relation candidate
        while index < max_iter:
            # Prompt identification agent to generate a metamorphic relation candidate
            i = min(index, len(agent_iden.config["prompts"]["user"]) - 1)
            prompt_template = PromptTemplate.from_file(agent_iden.config["prompts"]["user"][i])
            usr_prompt = prompt_template.invoke(replacements).to_string()
            response = agent_iden.instance.invoke(
                {"messages": [{"role": "user", "content": usr_prompt}]},
                config=RunnableConfig({"configurable": {"thread_id": thread_id_dict["iden"]}}),
            )

            # Extract metamorphic relation candidate
            candidate = get_first_code_block(response["messages"][-1].content)

            # Prompt calibration agents to verify the MR candidate
            # TODO:It can be executed in parallel
            cali_res_lst = list()
            for agent in agent_cali:
                i = min(index, len(agent.config["prompts"]["user"]) - 1)
                prompt_template = PromptTemplate.from_file(agent.config["prompts"]["user"][i])
                usr_prompt = prompt_template.partial(**replacements).invoke({"gen_mrc": candidate}).to_string()
                response = agent.instance.invoke(
                    {"messages": [{"role": "user", "content": usr_prompt}]},
                    config=RunnableConfig({"configurable": {"thread_id": thread_id_dict["cali"][index]}}),
                )
                cali_res = get_first_code_block(response["messages"][-1].content)
                if "invalid" in cali_res.lower():
                    cali_res_lst.append(False)
                else:
                    cali_res_lst.append(True)

            # TODO: Calculate confidence score of calibration
            score = calculate_score(agent_cali, cali_res_lst, calc_method)

            # TODO: If confidence score less than threshold, collect & distill the error messages,
            # else, open a new chat to generate a new MR candidate

            index += 1

        state = agent_iden.instance.get_state(config=RunnableConfig({"configurable": {"thread_id": thread_id_dict["iden"]}})).values
        for message in state["messages"]:
            message.pretty_print()

        cnt += 1

    OKF("We're done here!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MR Identification via LLM, CoT, and RAG")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    args = parser.parse_args()
    usr_cfg = dict()
    with open(args.config, "r", encoding="utf-8") as f:
        usr_cfg = json.load(f)
    main(usr_cfg)
