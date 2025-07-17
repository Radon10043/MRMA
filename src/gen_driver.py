"""
Author       : Radon
Date         : 2025-07-10 17:43:16
LastEditors  : Radon
LastEditTime : 2025-07-17 12:36:04
Description  : Generate test driver for encoded-MRCs
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig

from fake_code import *
from utils import *


class Driver:
    """Driver class for test driver generation."""

    def __init__(self, user_config: dict):
        """Initialize the Driver class with user configuration.

        Parameters
        ----------
        user_config : dict
            A dictionary containing user configuration, including the agent configuration,
            candidate file path, build settings, etc.
        """
        self.user_config = user_config
        self.replacements = user_config.get("replacements", {})
        self.cand_path = user_config["candidate"]
        self.ext = Path(self.cand_path).suffix[1:]  # Remove the leading dot from the file extension
        self.uuid = uuid.uuid4().hex[:8]  # Unique identifier for the driver instance

    def preprocessing(self):
        """Preprocessing for the driver generation, including update candidate code with prefix."""
        config_build = self.user_config.get("build", {})
        code = Path(self.cand_path).read_text(encoding="utf-8")
        prefix = config_build.get("prefix", "")
        code = prefix + "\n" + code
        code = f"```{self.ext}\n{code}\n```"  # Wrap code in fenced code block with language tag
        self.replacements["candidate"] = code
        self.replacements["additional_reqs"] = str()

    def update_replacements(self, key: str, value: str):
        """Update a specific key in the replacements dictionary with a new value.

        Parameters
        ----------
        key : str
            The key in the replacements dictionary to be updated.
        value : str
            The new value to set for the specified key.
        """
        self.replacements[key] = value

    def save(self, code: str, out_dir: str):
        """Save the generated test driver code to a file.

        Parameters
        ----------
        code : str
            The code to be saved as a test driver.
        """
        # TODO: Do we need format the code before saving?
        out_path = os.path.join(out_dir, "test_driver." + self.ext)
        Path(out_path).write_text(code, encoding="utf-8")


class DriverCpp(Driver):
    """Driver class for C++ test driver generation."""

    def build(self, code: str) -> tuple[bool, str]:
        """Build a C++ test driver from the provided code.

        Parameters
        ----------
        code : str
            The C++ code to be compiled as a test driver.

        Returns
        -------
        tuple[bool, str]
            A tuple containing a boolean indicating success or failure, and a string with error messages if any.
        """
        cxx = "g++"
        filepath = f"/tmp/test_driver.{self.uuid}.cpp"
        gtest_dir = os.getenv("GTEST_DIR")
        Path(filepath).write_text(code, encoding="utf-8")

        cmd = [
            cxx,
            filepath,
            "-std=c++17",
            "-pthread",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-o",
            "/tmp/test_driver",
            "-isystem",
            f"{gtest_dir}/googletest/include",
            f"{gtest_dir}/build/lib/libgtest.a",
            f"{gtest_dir}/build/lib/libgtest_main.a",
        ]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return result.returncode == 0, result.stderr


class DriverJava(Driver):
    """Driver class for Java test driver generation."""

    def preprocessing(self):
        """Perform preprocessing with additional requirements for Java."""
        super().preprocessing()
        additional_reqs = str()
        download_path = os.path.join(str(os.getenv("PROJECT")), "downloads")
        avaliable_jars = [file for file in os.listdir(download_path) if file.endswith(".jar")]
        additional_reqs = "- The name of the class should be `DriverTest`.\n"
        additional_reqs += "- The following jar packages are available for you: " + ", ".join(avaliable_jars) + ".\n"
        self.replacements["additional_reqs"] = additional_reqs

        # Create a Java toy
        self.build_dir = f"/tmp/test_driver_java_{self.uuid}"
        self.create_java_project(self.build_dir)

        # Copy the source files to the src directory if the key `srcdir` exists in the build config.
        config_build = self.user_config.get("build", {})
        srcdir = config_build.get("srcdir", None)
        if srcdir:
            shutil.copytree(srcdir, os.path.join(self.build_dir, "src"), dirs_exist_ok=True)


    def create_java_project(self, build_dir: str):
        """Create a basic Java project structure for the test driver.

        Parameters
        ----------
        build_dir : str
            The directory where the Java project structure will be created.
        """
        # Clean up the previous driver directory and create a new one
        project_dir = str(os.getenv("PROJECT"))
        shutil.rmtree(build_dir, ignore_errors=True)
        os.makedirs(build_dir, exist_ok=True)

        # Classical java project path, didn't it?
        os.makedirs(os.path.join(build_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(build_dir, "lib"), exist_ok=True)
        os.makedirs(os.path.join(build_dir, "test"), exist_ok=True)
        for f in os.listdir(os.path.join(project_dir, "downloads")):
            src = os.path.join(project_dir, "downloads", f)
            dst = os.path.join(build_dir, "lib", f)
            shutil.copy2(src, dst) if src.endswith(".jar") else None

    def build(self, code: str) -> tuple[bool, str]:
        """Build a Java test driver from the provided code.

        Parameters
        ----------
        code : str
            The Java code to be compiled as a test driver.

        Returns
        -------
        tuple[bool, str]
            A tuple containing a boolean indicating success or failure, and a string with error messages if any.
        """
        # Write the code to a Java file
        filepath = os.path.join(self.build_dir, "test", "DriverTest.java")
        Path(filepath).write_text(code, encoding="utf-8")

        # Compile .java file to .class file
        java_files = glob.glob(os.path.join(self.build_dir, "src", "*.java"))
        cmd = [
            "javac",
            "-d",
            "bin",
            "-cp",
            "lib/*",
            "test/DriverTest.java",
            *java_files,
        ]
        result = subprocess.run(
            cmd,
            cwd=self.build_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return result.returncode == 0, result.stderr

    def save(self, code: str, out_dir: str):
        """Save the generated Java test driver code to a file, just copy the whole directory
        of "/tmp/test_driver_java" to the output directory simply.

        Parameters
        ----------
        code : str
            The code to be saved as a test driver.
        out_dir : str
            The output directory where the test driver will be saved.
        """
        driver_dir = os.path.join(out_dir, "test_driver")
        shutil.copytree(self.build_dir, driver_dir, dirs_exist_ok=True)


class DriverPython(Driver):
    """Driver class for Python test driver generation."""

    def preprocessing(self):
        """Perform preprocessing with additional requirements for Python."""
        super().preprocessing()
        additional_reqs = str()
        additional_reqs += "- Please implement the main function to start the testing.\n"
        self.replacements["additional_reqs"] = additional_reqs

    def build(self, code: str) -> tuple[bool, str]:
        """Build a Python test driver from the provided code.

        Parameters
        ----------
        code : str
            The Python code to be compiled as a test driver.

        Returns
        -------
        tuple[bool, str]
            A tuple containing a boolean indicating success or failure, and a string with error messages if any.
        """
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            err = f"SyntaxError: {e.msg} at line {e.lineno}, column {e.offset}"
            return False, err
        except BaseException as e:
            FATAL(f"Unexpected error during Python code compilation: {e}")
        return True, str()


def main(user_config: dict):
    """Generate a test driver based on the provided user configuration.

    Parameters
    ----------
    user_config : dict
        A dictionary containing user configuration, including the agent configuration,
        candidate file path, build settings, etc.
    """
    # Initialize reference driver based on the candidate file extension
    cand_path = user_config["candidate"]
    ext = Path(cand_path).suffix[1:]  # Remove the leading dot from the file extension
    driver = None
    if ext == "cpp":
        driver = DriverCpp(user_config)
    elif ext == "java":
        driver = DriverJava(user_config)
    elif ext == "py":
        driver = DriverPython(user_config)
    else:
        raise ValueError(f"Unsupported file extension: {ext}.")
    driver.preprocessing()

    # Init an driver generation agent and assign it an unique thread ID for chating iteratively
    ACTF("Initializing driver generation agent ...")
    config_agent = user_config["agent"]
    agent = Agent(config=config_agent, tools=[], replacements=driver.replacements)
    agent.runnable_config = RunnableConfig({"configurable": {"thread_id": uuid.uuid4().hex}})

    index = 0
    max_iter = user_config.get("max_iter", 10)
    usr_pts = config_agent["prompts"]["user"]
    gen_succ = False
    compl_code = str()

    # Start prompting the agent to generate complete code
    while index < max_iter and not gen_succ:
        ACTF(f"Prompting agent to generate test driver code, iteration {index + 1} ...")
        i = min(index, len(usr_pts) - 1)  # Use the last prompt if index exceeds available prompts
        pt = PromptTemplate.from_file(usr_pts[i])
        prompt = pt.invoke(driver.replacements).to_string()
        response = agent.instance.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=agent.runnable_config,
        )
        compl_code = get_first_code_block(response["messages"][-1].content)
        compl_code = remove_code_fences(compl_code)
        gen_succ, error_messages = driver.build(compl_code)
        driver.update_replacements("error_messages", error_messages)
        index += 1
        if not gen_succ:
            WARNF("Failed to build the generated test driver, retrying ...")

    # If the generation is successful, save the generated code to the local
    out_dir = os.path.dirname(cand_path)
    if gen_succ:
        driver.save(compl_code, out_dir)
        OKF(f"Test driver generated successfully after {index} iterations, check it at: {out_dir}")
    else:
        BADF(f"Failed to generate a valid test driver after {max_iter} iterations.")

    # Save the agent's messages to a file
    save_agent_messages(agent, os.path.join(out_dir, "agent_driver_messages.txt"))

    OKF("We're done here!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test driver for encoded-MRCs")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    args = parser.parse_args()
    load_dotenv()
    cfg_text = Path(args.config).read_text(encoding="utf-8")
    usr_cfg = json.loads(os.path.expandvars(cfg_text))
    main(usr_cfg)
