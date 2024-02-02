import logging

import ctrlability.util.printing as printing
from ctrlability.util.argparser import parse_arguments

log = logging.getLogger(__name__)


def main():
    from ctrlability.core import bootstrapper

    stream_handlers = bootstrapper.boot()

    if log.isEnabledFor(logging.DEBUG):
        from ctrlability.util.tree_print import TreePrinter

        tree_printer = TreePrinter(stream_handlers, bootstrapper._mapping_engine)
        tree_printer.print_representation()

    # run the main loop of the app infinitely
    while True:
        try:
            for stream in stream_handlers:
                stream.process(None)
        except KeyboardInterrupt:
            log.info("KeyboardInterrupt: Exiting...")
            break


def show_version():
    from ctrlability import __version__

    printing.print_line()
    print("CTRLABILITY - Controller for people with motor disabilities")
    print(f"Version: {__version__}")
    exit(0)


def setup():
    # set the config file path from the arguments
    from ctrlability.core.config_parser import ConfigParser

    ConfigParser.CONFIG_PATH = args.config_file


if __name__ == "__main__":
    args = parse_arguments()

    if args.show_version:
        show_version()

    setup()

    main()
