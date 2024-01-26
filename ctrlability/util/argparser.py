import argparse
import logging

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
    "-c",
    "--config",
    dest="config_file",
    default="config.yaml",
    help="Set the config file (default: config.yaml)",
)

parser.add_argument(
    "-v",
    "--version",
    action="store_true",
    dest="show_version",
    help="Show the version of CTRLABILITY and exit.",
)


def parse_arguments():
    """Parse the arguments and set the log level"""
    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s %(name)s [%(levelname)s]: %(message)s", level=args.log_level)
    logging.debug("Debug logging enabled")
    return args
