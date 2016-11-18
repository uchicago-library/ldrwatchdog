
from argparse import ArgumentParser
from os import _exit

from ldrwatchdog.app.fixitychecker import main

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a command line tool to run a fixity check run on the contents of longTermStorage"

if __name__ == "__main__":
    arguments = ArgumentParser(description="a command-line tool to check fixity of files in longTermStorage",
                               epilog="Copyright University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
    arguments.add_argument("max_num_files", action='store', type=int, help="maximum allowed number of files for this run")
    arguments.add_argument("-b", "--max_bytes_to_read", action='store', type=int, help="total number of bytes to read for this run")
    parsed_args = arguments.parse_args()
    _exit(main(parsed_args.max_num_files, parsed_args.max_bytes_to_read))
