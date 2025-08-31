import argparse
import itertools
import json
import os
import smtplib
import sys
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

import src.gen_candidate
import src.gen_driver

from .utils import *


def send_email(subject: str, body: str, receiver: str):
    """Send an email notification.

    Parameters
    ----------
    subject : str
        Subject of the email
    body : str
        Body content of the email
    receiver : str
        Email address to send the notification to
    """
    msg = MIMEMultipart()
    sender = os.getenv("EMAIL_SENDER")
    passwd = os.getenv("EMAIL_PASSWORD")
    host = os.getenv("EMAIL_HOST")
    port = os.getenv("EMAIL_PORT")
    if sender is None:
        FATAL("Email sender is not configured in .env file.")
    elif passwd is None:
        FATAL("Email password is not configured in .env file.")
    elif host is None:
        FATAL("Email host is not configured in .env file.")
    elif port is None:
        FATAL("Email port is not configured in .env file.")
    msg["From"] = sender  # type: ignore
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP(host, port)  # type: ignore
        server.starttls()
        server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))  # type: ignore
        server.sendmail(msg["From"], msg["To"], msg.as_string())
        server.quit()
    except Exception as e:
        FATAL(f"Failed to send email: {e}")


def get_existing_cands(dir: str) -> list[str]:
    """Get existing mr candidates under dir.

    Parameters
    ----------
    dir : str
        Directory to search for mr candidates

    Returns
    -------
    list[str]
        List of absolute paths to existing mr candidates
    """
    existing_mrs = list()
    if not Path(dir).exists():
        return []
    cands = Path(dir).rglob("mr_candidate*")
    for file in cands:
        existing_mrs.append(os.path.abspath(file))
    return existing_mrs


def gen_cand_close(project_path: str, cali_linear: bool, suts: list[str], temperature: float, top_p: float):
    """Generate candidate MRs via the close group.

    Parameters
    ----------
    project_path : str
        Path to the project.
    cali_linear : bool
        Whether to use calibration linearization.
    suts : list[str]
        List of SUTs to process.
    temperature : float
        Temperature to use for MR identification.
    top_p : float
        Top-p to use for MR identification.
    """
    for sut in suts:
        SAYF(f"==================== [GROUP: close / SUT: {sut} / temperature: {temperature} / top_p: {top_p}] ====================\n")
        cfg = default_close_config(sut)
        cfg["agent_iden"]["temperature"] = temperature
        cfg["agent_iden"]["top_p"] = top_p
        out_dir = os.path.join(project_path, "workdir", "RQ6", f"close-temp_{temperature:.1f}-top_{top_p:.1f}", sut)
        max_MRs = 10
        existing_mrs = get_existing_cands(out_dir)
        max_MRs -= len(existing_mrs)
        if max_MRs <= 0:
            WARNF(f"Skipping {sut} with temperature {temperature} and top_p {top_p} as it already has enough candidates.")
            continue
        cfg["existing_mrs"] = existing_mrs
        cfg["max_MRs"] = max_MRs
        cfg["output"] = out_dir
        cfg["cali_linear"] = cali_linear
        src.gen_candidate.main(cfg)


def gen_cand_open(project_path: str, cali_linear: bool, suts: list[str], temperature: float, top_p: float):
    """Generate candidate MRs via the open group.

    Parameters
    ----------
    project_path : str
        Path to the project.
    cali_linear : bool
        Whether to use calibration linearization.
    suts : list[str]
        List of SUTs to process.
    temperature : float
        Temperature to use for MR identification.
    top_p : float
        Top-p to use for MR identification.
    """
    for sut in suts:
        SAYF(f"==================== [GROUP: open / SUT: {sut} / temperature: {temperature} / top_p: {top_p}] ====================\n")
        cfg = default_open_config(sut)
        cfg["agent_iden"]["temperature"] = temperature
        cfg["agent_iden"]["top_p"] = top_p
        out_dir = os.path.join(project_path, "workdir", "RQ6", f"open-temp_{temperature:.1f}-top_{top_p:.1f}", sut)
        max_MRs = 10
        existing_mrs = get_existing_cands(out_dir)
        max_MRs -= len(existing_mrs)
        if max_MRs <= 0:
            WARNF(f"Skipping {sut} with temperature {temperature} and top_p {top_p} as it already has enough candidates.")
            continue
        cfg["existing_mrs"] = existing_mrs
        cfg["max_MRs"] = max_MRs
        cfg["output"] = out_dir
        cfg["cali_linear"] = cali_linear
        src.gen_candidate.main(cfg)


def gen_cand_hybrid(project_path: str, cali_linear: bool, suts: list[str], temperature: float, top_p: float):
    """Generate candidate MRs via the hybrid group.

    Parameters
    ----------
    project_path : str
        Path to the project.
    cali_linear : bool
        Whether to use calibration linearization.
    suts : list[str]
        List of SUTs to process.
    temperature : float
        Temperature to use for MR identification.
    top_p : float
        Top-p to use for MR identification.
    """
    for sut in suts:
        SAYF(f"==================== [GROUP: hybrid / SUT: {sut} / temperature: {temperature} / top_p: {top_p}] ====================\n")
        cfg = default_hybrid_config(sut)
        cfg["agent_iden"]["temperature"] = temperature
        cfg["agent_iden"]["top_p"] = top_p
        out_dir = os.path.join(project_path, "workdir", "RQ6", f"hybrid-temp_{temperature:.1f}-top_{top_p:.1f}", sut)
        max_MRs = 10
        existing_mrs = get_existing_cands(out_dir)
        max_MRs -= len(existing_mrs)
        if max_MRs <= 0:
            WARNF(f"Skipping {sut} with temperature {temperature} and top_p {top_p} as it already has enough candidates.")
            continue
        cfg["existing_mrs"] = existing_mrs
        cfg["max_MRs"] = max_MRs
        cfg["output"] = out_dir
        cfg["cali_linear"] = cali_linear
        src.gen_candidate.main(cfg)


def RQ6(args: argparse.Namespace):
    project_path = str(os.getenv("PROJECT"))
    cali_linear = args.linear
    group = args.group
    temperature = args.temperature
    top_p = args.top_p
    sut_root = os.path.join(project_path, "Empirical-Study-LLM-MR", "software-under-test")
    suts = [d for d in os.listdir(sut_root) if os.path.isdir(os.path.join(sut_root, d))]
    suts.sort()

    # Close group
    if group == "close" or group == "all":
        gen_cand_close(project_path, cali_linear, suts, temperature, top_p)

    # Open group
    if group == "open" or group == "all":
        gen_cand_open(project_path, cali_linear, suts, temperature, top_p)

    # Hybrid group
    if group == "hybrid" or group == "all":
        gen_cand_hybrid(project_path, cali_linear, suts, temperature, top_p)


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
        cands = get_existing_cands(os.path.join(workdir, sut))
        for cand in cands:
            SAYF(f"========== [MR cand: {cand}] ==========\n")
            drvs = list(Path(cand).parent.rglob("test_driver*"))
            if len(drvs) > 0:
                WARNF(f"Skipping {cand} as test_driver already exists.")
                continue
            cfg["candidate"] = cand
            src.gen_driver.main(cfg)


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="MR-CoT-RAG Experiment Runner")
    parser.add_argument("--email", type=str, default="", help="Email address to send notifications to")
    subparsers = parser.add_subparsers(title="RQx", required=True)

    rq6_parser = subparsers.add_parser("RQ6", help="Run RQ6 experiment")
    rq6_parser.add_argument("--group", type=str, choices=["close", "open", "hybrid", "all"], help="Which group to use to identify MRs")
    rq6_parser.add_argument("--temperature", type=float, choices=[0.5, 1.0, 1.5], help="Temperature to use for MR identification")
    rq6_parser.add_argument("--top_p", type=float, choices=[0.5, 1.0], help="Top-p to use for MR identification")
    rq6_parser.add_argument("--linear", action="store_true", help="Whether to use linear calibration")
    rq6_parser.set_defaults(func=RQ6)

    driver_parser = subparsers.add_parser("driver", help="Prompt llm to generate the driver")
    driver_parser.add_argument("--path", type=str, required=True, help="Path including software under test and corresponding mr candidates")
    driver_parser.set_defaults(func=driver)

    args = parser.parse_args()
    try:
        args.func(args)
        if len(args.email) > 0:
            subject = "MR-CoT-RAG Experiment Success"
            body = f"Hi,\n\nThe experiment completed successfully.\n\n"
            body += "Program args: " + " ".join(sys.argv) + "\n\n"
            body += "Best regards,\nMR-CoT-RAG Experiment Runner"
            send_email(subject, body, args.email)
    except BaseException as e:
        traceback.print_exc()
        if len(args.email) > 0:
            subject = "MR-CoT-RAG Experiment Failed"
            body = f"Hi,\n\nAn error occurred during the experiment:\n\n{e}\n\n"
            body += f"Traceback:\n{traceback.format_exc()}\n\n"
            body += "Program args: " + " ".join(sys.argv) + "\n\n"
            body += "\n\nPlease check the logs for more details.\n\nBest regards,\nMR-CoT-RAG Experiment Runner"
            send_email(subject, body, args.email)
