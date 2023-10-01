import argparse
import logging as log

# Create the argument parser
parser = argparse.ArgumentParser(description="CTRLABILITY - Controller for people with motor disabilities")
parser.add_argument(
    "-l",
    "--log",
    dest="log_level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="INFO",
    help="Set the log level (default: INFO)",
)

parser.add_argument(
    "-r",
    "--resolution",
    dest="resolution",
    choices=["MIN", "MAX"],
    default="MIN",
    help="Set the resolution of the camera (default: 640 x 480)",
)


def parse_arguments():
    """Parse the arguments and set the log level"""
    args = parser.parse_args()
    log.basicConfig(format="%(asctime)s [%(levelname)s]: %(message)s", level=args.log_level)
    return args
