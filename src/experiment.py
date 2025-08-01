import argparse
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import sys
import traceback
import smtplib

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


def RQ6(args: argparse.Namespace):
    project_path = str(os.getenv("PROJECT"))
    sut_root = os.path.join(project_path, "Empirical-Study-LLM-MR", "software-under-test")
    suts = [d for d in os.listdir(sut_root) if os.path.isdir(os.path.join(sut_root, d))]
    suts.sort()
    for sut in suts:
        for temperature in [0.5, 1.0, 1.5]:
            for top_p in [0.5, 1.0]:
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
    parser = argparse.ArgumentParser(description="MR-CoT-RAG Experiment Runner")
    parser.add_argument("--email", type=str, default="", help="Email address to send notifications to")
    subparsers = parser.add_subparsers(title="RQx", required=True)

    rq6_parser = subparsers.add_parser("RQ6", help="Run RQ6 experiment")
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
