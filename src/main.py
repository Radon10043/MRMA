"""
Author       : Radon
Date         : 2025-06-24 17:28:25
LastEditors  : Radon
LastEditTime : 2025-06-27 21:12:45
Description  : MR Identification via LLM, CoT, and RAG
"""

import argparse
import json
import math
import uuid

from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import TextLoader
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

    def __init__(self, config: dict, tools: list):
        """Initialize an agent with a chat model and tools.

        Parameters
        ----------
        config : dict
            Configuration dictionary.
        tools : list
            List of tools to be used by the agent.
        """
        self.llm = init_chat_model(
            model=config.get("model"),
            temperature=config.get("temperature", 1.0),
            model_provider="openai",
            top_p=config.get("top_p", 0.9),
        )
        sys_prompt = str()
        with open(config["prompts"]["system"], "r", encoding="utf-8") as f:
            sys_prompt = f.read()
        memory = MemorySaver()
        self.instance = create_react_agent(
            model=self.llm,
            tools=tools,
            checkpointer=memory,
            prompt=sys_prompt,
        )


def calculate_score_exp(agents: list[Agent]) -> float:
    # TODO: Implement the exponential confidence score calculation
    return 0.0


def calculate_score_rec(agents: list[Agent]) -> float:
    # TODO: Implement the recursive confidence score calculation
    return 0.0


def calculate_score(agents: list[Agent], method: str) -> float:
    """Confidence score calculation based on the specified method.

    Parameters
    ----------
    method : str
        The method for confidence score calculation. Options are "EXP", "REC", etc.

    Returns
    -------
    float
        The calculated confidence score.
    """
    if method == "EXP":
        return calculate_score_exp(agents)
    elif method == "REC":
        return calculate_score_rec(agents)
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
    calc_method = usr_config.get("confidence_calc", "EXP")
    max_mrs, max_iter = usr_config["max_MRs"], usr_config["max_iter"]

    # Initialize vector store
    init_vector_store(config_iden.get("external_corpus"))

    # Initialize identification, calibration, and distilliation agents
    agent_iden = Agent(config_iden, [retrieve])
    agent_distn = Agent(config_distn, [])
    agent_cali = list()
    for cfg in config_cali:
        agent = Agent(cfg, [])
        agent_cali.append(agent)

    # Start metamorphic relation identification loop
    cnt = 0
    while cnt < max_mrs:
        index = 0

        # Generate unique thread IDs for chating iteratively
        thread_id_dict = dict()
        thread_id_dict["iden"] = uuid.uuid4().hex
        thread_id_dict["dist"] = uuid.uuid4().hex
        thread_id_dict["cali"] = [uuid.uuid4().hex for _ in range(len(agent_cali))]

        # Start a new chat to identify one metamorphic relation candidate
        while index < max_iter:
            # Prompt identification agent to generate a metamorphic relation candidate
            usr_prompt = str()
            i = min(index, len(config_iden["prompts"]["user"]) - 1)
            with open(config_iden["prompts"]["user"][i], "r", encoding="utf-8") as f:
                usr_prompt = f.read()
            response = agent_iden.instance.invoke(
                {"messages": [{"role": "user", "content": usr_prompt}]},
                config=RunnableConfig({"configurable": {"thread_id": thread_id_dict["iden"]}}),
            )

            # TODO: Extract metamorphic relation candidate

            # TODO: Prompt calibration agents to verify the MR candidate

            # TODO: Calculate confidence score of calibration

            # TODO: If confidence score less than threshold, collect & distill the error messages,
            # else, open a new chat to generate a new MR candidate

            index += 1

        state = agent_iden.instance.get_state(config=RunnableConfig({"configurable": {"thread_id": thread_id_dict["iden"]}})).values
        for message in state["messages"]:
            message.pretty_print()

        cnt += 1

    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MR Identification via LLM, CoT, and RAG")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    args = parser.parse_args()
    usr_cfg = dict()
    with open(args.config, "r", encoding="utf-8") as f:
        usr_cfg = json.load(f)
    main(usr_cfg)
