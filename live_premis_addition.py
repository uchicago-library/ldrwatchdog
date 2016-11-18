from argparse import ArgumentParser
from os import _exit

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a command line tool to find all premis records in longTermStorage and if not already in livePremis copy the file into livePremis"

if __name__ == "__main__":
    arguments = ArgumentParser(description="A tool to check for new premis records in longTermStorage",
                               epilog="Copyright University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
    arguments.add_argument("longterm_root", action="store", help="the location of longTermStorage")
    arguments.add_argument("livepremis_root", action="store", help="the locaiton of livePremis")
    parsed_args = arguments.parse_args()
    cached_file = join(parsed_args.livepremis_root, "cached.json")
    _exit(main(cached_file, parsed_args.longterm_root, parsed_args.livepremis_root))
