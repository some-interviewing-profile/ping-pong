import argparse
import json
import logging
import os
import requests
import signal
import subprocess
import sys
import time


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


PIDFILE = "pid.json"


def read_pid_file(filename):
    try:
        with open(filename) as f:
            return json.load(f)
    except Exception as e:
        logger.error("failed to read pid file: %s", e)


def write_pid_file(filename, pid):
    with open(filename, "w") as f:
        json.dump(pid, f)


def delete_pid_file(filename):
    try:
        os.remove(filename)
    except Exception as e:
        logger.error("failed to delete pid file: %s", e)


def preexec():
    signal.signal(signal.SIGHUP, signal.SIG_IGN)


def start_handler(args):
    logger.info("start %s", args.pong_time_ms)
    pid = read_pid_file(PIDFILE)
    if pid is not None:
        logger.warning("already running")
        return

    env = {
        "DO_INITIAL_PING": "false",
        "OTHER_ENDPOINT": "http://localhost:10000/ping",
        "PONG_TIME_MS": str(args.pong_time_ms),
    }
    second = subprocess.Popen(
        ["uvicorn", "server:app", "--port", "20000"],
        stdout=open("second.log", "w"),
        stderr=subprocess.STDOUT,
        env=os.environ | env,
        preexec_fn=preexec,
    )
    time.sleep(1)

    env["DO_INITIAL_PING"] = "true"
    env["OTHER_ENDPOINT"] = "http://localhost:20000/ping"
    first = subprocess.Popen(
        ["uvicorn", "server:app", "--port", "10000"],
        stdout=open("first.log", "w"),
        stderr=subprocess.STDOUT,
        env=os.environ | env,
        preexec_fn=preexec,
    )

    write_pid_file(
        PIDFILE,
        {
            "second": second.pid,
            "first": first.pid,
        },
    )


def pause_handler(_):
    logger.info("pause")
    pid = read_pid_file(PIDFILE)
    if pid is None:
        logger.error("not running")
        return
    requests.post("http://localhost:10000/pause")
    requests.post("http://localhost:20000/pause")


def resume_handler(_):
    logger.info("resume")
    pid = read_pid_file(PIDFILE)
    if pid is None:
        logger.error("not running")
        return
    requests.post("http://localhost:10000/resume")
    requests.post("http://localhost:20000/resume")


def stop_handler(_):
    logger.info("stop")
    pid = read_pid_file(PIDFILE)
    if pid is None:
        logger.error("not running")
        return
    subprocess.run(f"kill {pid['first']} {pid['second']}", shell=True)
    delete_pid_file(PIDFILE)


def main():
    args = argparse.ArgumentParser()
    subs = args.add_subparsers(required=True)

    start = subs.add_parser("start")
    start.add_argument("pong_time_ms", type=int)
    start.set_defaults(func=start_handler)

    pause = subs.add_parser("pause")
    pause.set_defaults(func=pause_handler)

    resume = subs.add_parser("resume")
    resume.set_defaults(func=resume_handler)

    stop = subs.add_parser("stop")
    stop.set_defaults(func=stop_handler)

    namespace = args.parse_args()
    namespace.func(namespace)


if __name__ == "__main__":
    main()
