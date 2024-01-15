import logging

import ctrlability.util.printing as printing
from ctrlability import __version__
from ctrlability.engine import bootstrapper
from ctrlability.engine.config_parser import ConfigParser
from ctrlability.util.argparser import parse_arguments

log = logging.getLogger(__name__)


def main():
    stream_handlers = bootstrapper.boot()

    if log.isEnabledFor(logging.DEBUG):
        from ctrlability.util.tree_print import TreePrinter

        tree_printer = TreePrinter(stream_handlers, bootstrapper._mapping_engine)
        tree_printer.print_representation()

    while True:
        for stream in stream_handlers:
            stream.process(None)


def show_version():
    printing.print_line()
    print("CTRLABILITY - Controller for people with motor disabilities")
    print(f"Version: {__version__}")
    exit(0)


if __name__ == "__main__":
    args = parse_arguments()

    if args.show_version:
        show_version()

    # set the config file path from the arguments
    ConfigParser.CONFIG_PATH = args.config_file

    main()
