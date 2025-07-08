FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /home

RUN apt update && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash && \
    apt install -y wget curl make cmake gcc g++ git python3 python3-dev python3-pip vim build-essential libssl-dev openssl libffi-dev graphviz libgraphviz-dev python3-sphinx nodejs cloc && \
    pip install IPython black isort beautifulsoup4 langchain-text-splitters langchain-community langgraph langchain-core langchain-openai pygraphviz marko sphinx sphinx-rtd-theme && \
    mkdir tools && pushd tools && \
    wget https://github.com/google/googletest/archive/refs/tags/v1.14.0.tar.gz && \
    tar zxvf v1.14.0.tar.gz && pushd googletest-1.14.0 && \
    mkdir build && pushd build && \
    cmake .. && make && \
    popd && popd && rm v1.14.0.tar.gz && popd && \
    npm install -g @google/gemini-cli