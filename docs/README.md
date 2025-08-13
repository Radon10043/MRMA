# MR-CoT-RAG

Welcome to the MR-CoT-RAG project! This document will guide you through setting up and running the experiments. Let's get started! 😊

## Prerequisites 🛠️

### Build the docker

First, clone the repository. Don't forget the submodules!

```bash
git clone --recurse-submodules https://github.com/Radon10043/MR-CoT-RAG
```

If you forgot to include the submodules during the clone, you can initialize them like this:

```bash
cd MR-CoT-RAG
git submodule update --init --recursive
```

Next, build the Docker image. You can add the `--network host` flag if needed.

```bash
docker build -t mr-cot-rag:latest -f docker/Dockerfile .
```

Now, run the Docker container:

```bash
docker run -d -v .:/MR-CoT-RAG --name mr-cot-rag mr-cot-rag:latest tail -f /dev/null
```

Finally, access the container using vscode's remote development features or with `docker exec`. The repository will be located in the root directory.

```bash
docker exec -it mr-cot-rag bash
cd /MR-CoT-RAG  # Run this inside the container
```

### Set environment variables

We recommend storing environment variables in a `.env` file at the root of the project. The application will automatically load these variables. To get started, you should set the `PROJECT` and `GTEST_DIR` environment variables.

```env
PROJECT=/vol/MR-CoT-RAG
GTEST_DIR=/home/tools/googletest-1.14.0
```

## Running the Workflow 🚀

### Metamorphic Relation (MR) Identification

> [!NOTE]
> Before you begin, please run `make download build_sir patch_sut` from the root of the repository.

Our approach uses a multi-agent method to identify Metamorphic Relations (MRs) contained in the software under test. One agent generates an MR candidate, while other agents calibrate it, providing feedback for refinement until a satisfactory result is achieved.

To start the MR identification process, run `src/gen_candidate.py`. This script takes a JSON configuration file as input. Here's a breakdown of the configuration options:

- `agent_iden`: Configuration for the identification agent.
  - `model`: The name of the LLM to use.
  - `temperature`: The sampling temperature for the LLM (default: 1.0).
  - `top_p`: The nucleus sampling probability (default: 1.0).
  - `external_corpus`: Path to an external corpus for RAG to improve output quality.
  - `base_url`: The base URL for the LLM API (defaults to the `OPENAI_API_BASE` environment variable).
  - `api_key`: The API key for the LLM (defaults to the `OPENAI_API_KEY` environment variable).
  - `prompts`: The prompts to send to the agent.
    - `system`: Path to the system prompt file.
    - `user`: A list of paths to user prompt files. These are sent sequentially. If the sequence is exhausted, the last prompt is reused.
- `agent_cali`: A list of agents used to calibrate the MR candidate(s). The configuration is similar to `agent_iden`, but it does not support `external_corpus`.
- `agent_distn`: Similar to `agent_iden`, but also does not support `external_corpus`.
- `replacements`: A dictionary for substituting placeholders (like `{key}`) in prompts with specified values.
- `existing_mrs`: Path to a file of existing MRs to prevent generating duplicates.
- `socre_calc`: The confidence score calculation method. Supported methods are `EXP`, `LOG`, `QUA`, and `LIN`.
- `max_MRs`: The maximum number of MR candidates to generate (iteratively).
- `max_iter`: The maximum number of calibration iterations for a single MR candidate.
- `output`: The directory where output will be saved. Each MR candidate is stored in a timestamped directory.

We've provided some example configuration files under the `configs` directory (e.g., `XXX_candidate.json`). For example, to identify MRs for `Bsearch2`, run:

```bash
python3 -m src.gen_candidate --config configs/Bsearch2/Bsearch2_candidate.json
```

You can add the `--linear` flag to perform calibration sequentially instead of in parallel.

### Test Driver Generation

This step is optional but recommended, as a test driver helps verify the correctness of the MR candidate.

To generate a test driver, run `src/gen_driver.py`. This script iteratively prompts an LLM to create an executable test driver. If the generated driver fails to compile, the compiler errors are fed back to the LLM for correction. The configuration file is similar to the one for MR identification:

- `candidate`: Path to the MR candidate file.
- `agent`: Agent configuration, similar to `agent_iden` but without `external_corpus`.
- `build`: Build settings.
  - `prefix`: A prefix to add to the beginning of the candidate file.
  - `srcdir`: (For Java only) Files and directories under `srcdir` will be copied to `test_driver/src`.
- `max_iter`: The maximum number of generation attempts for the test driver.

We have also included configuration files for driver generation in the `configs` directory (e.g., `XXX_driver.json`). Using `Bsearch2` as an example again:

```bash
python3 -m src.gen_driver --config configs/Bsearch2/Bsearch2_driver.json
```

## Running Test Driver(s) 🧪

Once you have a test driver, you can run it. Here's an example with a driver written in C++:

```bash
make SRC=/path/to/test_driver.cpp build_cpp
make BIN=/path/to/test_driver.out run_cpp
# Or combine them into one command, whichever you prefer :)
# make SRC=/path/to/test_driver.cpp BIN=/path/to/test_driver.out build_cpp run_cpp
```

By default, the test driver will be executed 20 times, and the results will be printed to the terminal. You can also customize the number of repetitions:

```bash
make BIN=/path/to/test_driver.out REP=10 run_cpp
```

For Java and Python drivers, use these commands:

```bash
# Java
make JAVAPROJ=/path/to/test_driver build_java run_java
# Python
make PYTHON=/path/to/test_driver.py run_python
```

If you have multiple test drivers, you can run them all in batch with `scripts/batchrun.sh`:

```bash
scripts/batchrun.sh /path/to/dir
```

The `batchrun.sh` script recursively finds `test_driver.cpp`, `test_driver.py`, and `test_driver` folders, then compiles and runs them. The output is in CSV format, so you can easily redirect it to a `.csv` file.

## Reproducing the Experiment 🔬

You can reproduce our experiments by running `src/experiment.py`. For example:

```bash
python3 -m src.experiment RQ6
```

Here are the available subcommands and their arguments:
- `RQ6`:
  - `--linear`: Calibrate MR candidates linearly.
- `driver`:
  - `--path`: The root directory to recursively search for `mr_candidate` files.

### Email Notifications

Since experiments can be time-consuming, you can run them in the background and receive an email notification upon completion or if an error occurs. Make sure you have set the `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_SENDER`, and `EMAIL_PASSWORD` environment variables, either in a `.env` file or by exporting them in your terminal.

```bash
python3 -u -m src.experiment --email youremail@example.com RQ6
# Or run in the background
nohup python3 -u -m src.experiment --email youremail@example.com RQ6 &
```

### Time presentation

You can use `ts` to show time when logging.

```bash
python3 -u -m src.experiment --email youremail@example.com RQ6 | ts "[%Y-%m-%d %H:%M:%S]"
# Or run in the backgournd
# nohup python3 -u -m src.experiment --email youremail@example.com RQ6 | ts "[%Y-%m-%d %H:%M:%S]" > run.log &
```

## Disclaimer ✨

This document was originally written by Jiaming Zhang and polished by GitHub Copilot.