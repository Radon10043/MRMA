FROM ubuntu:22.04

SHELL ["/bin/bash", "-c"]

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV GTEST_DIR=/home/tools/googletest-1.14.0
ENV JAVA_HOME=/home/tools/jdk-24.0.1
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /home

RUN apt update && \
    apt install -y wget curl make cmake gcc g++ git python3 python3-dev python3-pip vim build-essential libssl-dev openssl libffi-dev graphviz libgraphviz-dev python3-sphinx nodejs cloc jq unzip && \
    pip install IPython black isort beautifulsoup4 langchain-text-splitters langchain-community langgraph langchain-core langchain-openai pygraphviz marko sphinx sphinx-rtd-theme parameterized scipy opencv-python seaborn python-calamine seaborn

# Install googletest
RUN mkdir tools && pushd tools && \
    wget https://github.com/google/googletest/archive/refs/tags/v1.14.0.tar.gz && \
    tar zxvf v1.14.0.tar.gz && pushd googletest-1.14.0 && \
    mkdir build && pushd build && \
    cmake .. && make && make install && \
    popd && popd && rm v1.14.0.tar.gz

# Install jdk-24.0.1
RUN pushd tools && \
    wget https://download.oracle.com/java/24/archive/jdk-24.0.1_linux-x64_bin.tar.gz && \
    tar xzvf jdk-24.0.1_linux-x64_bin.tar.gz && \
    rm jdk-24.0.1_linux-x64_bin.tar.gz