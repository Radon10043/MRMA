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

RUN apt update
RUN apt-get install -y wget curl make cmake gcc g++ git python3 python3-dev python3-pip python3.10-venv
RUN apt-get install -y vim build-essential libssl-dev openssl libffi-dev graphviz libgraphviz-dev
RUN apt-get install -y python3-sphinx nodejs cloc jq unzip moreutils lsb-release libgirepository1.0-dev
RUN apt-get install -y software-properties-common meson pkg-config libcairo2-dev libdbus-1-dev ripgrep
RUN apt-get install -y cairosvg

RUN pip install IPython black isort beautifulsoup4 pygraphviz marko sphinx sphinx-rtd-theme javalang
RUN pip install parameterized scipy opencv-python seaborn python-calamine seaborn timeout_decorator

RUN pip install langchain-text-splitters==0.3.9 langchain-community==0.3.29 langgraph==0.6.6
RUN pip install langchain-core==0.3.75 langchain-openai==0.3.32 clang==19.1.7
RUN pip install tree-sitter==0.25.2 tree-sitter-java==0.23.5

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

# Install LLVM-19
RUN wget https://apt.llvm.org/llvm.sh && \
    chmod +x llvm.sh && \
    ./llvm.sh 19 all && \
    rm llvm.sh

# Install fzf
RUN git clone --depth 1 https://github.com/junegunn/fzf.git /root/.fzf && \
    yes | /root/.fzf/install
