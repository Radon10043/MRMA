import argparse
import os

from dotenv import load_dotenv

import src.gen_candidate

from .utils import *


def RQ6(args):
    project_path = str(os.getenv("PROJECT"))
    sut_root = os.path.join(project_path, "Empirical-Study-LLM-MR", "software-under-test")
    suts = [d for d in os.listdir(sut_root) if os.path.isdir(os.path.join(sut_root, d))]
    for sut in suts:
        for temperature in [0.0, 0.5, 1.0, 1.5, 2.0]:
            for top_p in [0.0, 0.5, 1.0]:
                SAYF(f"==================== [SUT: {sut} / temperature: {temperature} / top_p: {top_p}] ====================\n")
                cfg = default_close_config(sut)
                cfg["agent_iden"]["temperature"] = temperature
                cfg["agent_iden"]["top_p"] = top_p
                out_dir = os.path.join(project_path, "workdir", "RQ6", f"close-temp_{temperature:.1f}-top_{top_p:.1f}", sut)
                if os.path.exists(out_dir) and len(os.listdir(out_dir)) >= 10:
                    WARNF(f"Skipping {sut} with temperature {temperature} and top_p {top_p} as it already has enough candidates.")
                    continue
                cfg["output"] = out_dir
                src.gen_candidate.main(cfg)


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the experiment.")
    subparsers = parser.add_subparsers(title="RQx", required=True)

    rq6_parser = subparsers.add_parser("RQ6", help="Run RQ6 experiment")
    rq6_parser.set_defaults(func=RQ6)

    args = parser.parse_args()
    args.func(args)
