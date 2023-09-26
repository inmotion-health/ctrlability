import argparse
import logging as log

# Create the argument parser
parser = argparse.ArgumentParser(description="CTRLABILITY - Controller for people with motor disabilities")
parser.add_argument(
    "-log",
    dest="log_level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="INFO",
    help="Set the log level (default: INFO)",
)


def parse_arguments():
    """Parse the arguments and set the log level"""
    args = parser.parse_args()
    log.basicConfig(format="%(asctime)s [%(levelname)s]: %(message)s", level=args.log_level)
    return args
