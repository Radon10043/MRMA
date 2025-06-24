FROM ubuntu:22.04

RUN apt update && \
    apt install -y wget make cmake gcc g++ git python3 python3-dev python3-pip vim build-essential libssl-dev openssl libffi-dev graphviz libgraphviz-dev && \
    pip install IPython black isort beautifulsoup4 langchain-text-splitters langchain-community langgraph langchain-core langchain-openai pygraphviz