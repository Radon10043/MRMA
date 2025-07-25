import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

import src.gen_candidate
import src.gen_driver

from .utils import *


def RQ6(args: argparse.Namespace):
    project_path = str(os.getenv("PROJECT"))
    sut_root = os.path.join(project_path, "Empirical-Study-LLM-MR", "software-under-test")
    suts = [d for d in os.listdir(sut_root) if os.path.isdir(os.path.join(sut_root, d))]
    suts.sort()
    for sut in suts:
        for temperature in [1.0]:
            for top_p in [1.0]:
                SAYF(f"==================== [SUT: {sut} / temperature: {temperature} / top_p: {top_p}] ====================\n")
                cfg = default_close_config(sut)
                cfg["agent_iden"]["temperature"] = temperature
                cfg["agent_iden"]["top_p"] = top_p
                out_dir = os.path.join(project_path, "workdir", "RQ6", f"close-temp_{temperature:.1f}-top_{top_p:.1f}", sut)
                max_MRs = 10
                existing_mrs = list()
                if os.path.exists(out_dir):
                    for root, _, files in os.walk(out_dir):
                        for file in files:
                            if file.startswith("mr_candidate"):
                                max_MRs -= 1
                                existing_mrs.append(os.path.abspath(os.path.join(root, file)))
                    if max_MRs <= 0:
                        WARNF(f"Skipping {sut} with temperature {temperature} and top_p {top_p} as it already has enough candidates.")
                        continue
                cfg["existing_mrs"] = existing_mrs
                cfg["max_MRs"] = max_MRs
                cfg["output"] = out_dir
                src.gen_candidate.main(cfg)


def driver(args: argparse.Namespace):
    project_path = str(os.getenv("PROJECT"))
    workdir = args.path
    cfg_tmpl_root = os.path.join(project_path, "configs")

    suts = os.listdir(workdir)
    suts.sort()
    for sut in suts:
        if not os.path.isdir(os.path.join(workdir, sut)):
            continue
        tmp = Path(os.path.join(cfg_tmpl_root, sut, f"{sut}_driver.json")).read_text(encoding="utf-8")
        cfg = json.loads(os.path.expandvars(tmp))
        cfg["agent"]["base_url"] = os.getenv("GOOGLE_OPENAI_API_BASE")
        cfg["agent"]["api_key"] = os.getenv("GOOGLE_API_KEY")
        for root, _, files in os.walk(os.path.join(workdir, sut)):
            for file in files:
                if not file.startswith("mr_candidate"):
                    continue
                cand_path = os.path.join(root, file)
                SAYF(f"========== [MR cand: {cand_path}] ==========\n")
                if os.path.exists(os.path.join(root, "test_driver")) or os.path.exists(os.path.join(root, "test_driver.py")) or os.path.exists(os.path.join(root, "test_driver.cpp")):
                    WARNF(f"Skipping {cand_path} as test_driver already exists.")
                    continue
                cfg["candidate"] = os.path.abspath(os.path.join(root, file))
                src.gen_driver.main(cfg)


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the experiment.")
    subparsers = parser.add_subparsers(title="RQx", required=True)

    rq6_parser = subparsers.add_parser("RQ6", help="Run RQ6 experiment")
    rq6_parser.set_defaults(func=RQ6)

    driver_parser = subparsers.add_parser("driver", help="Prompt llm to generate the driver")
    driver_parser.add_argument("--path", type=str, required=True, help="Path including software under test and corresponding mr candidates")
    driver_parser.set_defaults(func=driver)

    args = parser.parse_args()
    args.func(args)
