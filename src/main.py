"""
Author       : Radon
Date         : 2025-06-24 17:28:25
LastEditors  : Radon
LastEditTime : 2025-06-24 21:10:37
Description  : MR Identification via LLM, CoT, and RAG
"""

import argparse
import os

from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import TextLoader
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent

########## GLOBAL VARIABLES ##########
LLM = init_chat_model("gpt-4o-mini", model_provider="openai")
VECTOR_STORE = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-large"))
######################################


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
    retrived_docs = VECTOR_STORE.similarity_search(query)
    serialized = "\n\n".join((f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in retrived_docs))
    return serialized, retrived_docs


def generate(mstate: MessagesState) -> dict[str, list]:
    """Generate a response based on the messages state.

    Parameters
    ----------
    mstate : MessagesState
        The state of messages containing the conversation history.

    Returns
    -------
    dict[str, list]
        A dictionary containing a list of messages with the generated response.
    """
    recent_tool_msgs = list()
    for msg in reversed(mstate["messages"]):
        if msg.type == "tool":
            recent_tool_msgs.append(msg)
        else:
            break
        tool_msgs = recent_tool_msgs[::-1]
        docs_content = "\n\n".join(doc.content for doc in tool_msgs)
        sys_msg_content = "You are an expert for metamorphic relation identification. " "Use the following pieces of retrieved context to answer " "the question. If you don't know the answer, say that you " "don't know.\n\n" f"{docs_content}"
        conv_msgs = [m for m in mstate["messages"] if m.type in ("human", "system") or (m.type == "ai" and not m.tool_calls)]
        prompt = [SystemMessage(sys_msg_content)] + conv_msgs
    response = LLM.invoke(prompt)
    return {"messages": [response]}


def main():
    """Main function to perform metamorphic relation identification using LLM, CoT, and RAG."""
    # Load database
    md = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Bsearch2.md")
    loader = TextLoader(md, encoding="utf-8")
    docs = loader.load()

    # Split document
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    all_splits = text_splitter.split_documents(docs)

    # Save splits to vector store
    global VECTOR_STORE
    _ = VECTOR_STORE.add_documents(all_splits)

    # Initialize LLM and agent, then perform MR identification
    memory = MemorySaver()
    agent_executor = create_react_agent(
        model=LLM,
        tools=[retrieve],
        checkpointer=memory,
    )
    config = RunnableConfig({"configurable": {"thread_id": "foo"}})
    input_msg = "Please identify metamorphic relations of binary search algorithm."
    for event in agent_executor.stream(
        {"messages": [{"role": "user", "content": input_msg}]},
        stream_mode="values",
        config=config,
    ):
        event["messages"][-1].pretty_print()

    input_msg = "Please identify more different metamorphic relations."
    for event in agent_executor.stream(
        {"messages": [{"role": "user", "content": input_msg}]},
        stream_mode="values",
        config=config,
    ):
        event["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
