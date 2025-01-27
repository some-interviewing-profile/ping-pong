import argparse
import logging
import sys


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def start_handler(args):
    logger.info("start %s", args.pong_time_ms)


def pause_handler(args):
    logger.info("pause")


def resume_handler(args):
    logger.info("resume")


def stop_handler(args):
    logger.info("stop")


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
