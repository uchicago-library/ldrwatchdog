from argparse import ArgumentParser
from os import scandir, _exit
from os.path import exists, join, relpath
from json.decoder import JSONDecodeError
from uuid import uuid4

from ..lib.apistorage_public import *

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a command line tool to build new collection records for updating pre-pop acq interface collection list"

def main():
    arguments = ArgumentParser(description="A cli application to create new hierarchicalrecords for collections when necessary",
                               epilog="Copyright The University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
    arguments.add_argument("apistorage_root", action='store', type=str, help="The location of apistorage")
    parsed_args = arguments.parse_args()
    try:
        new_collection_titles = compare_title_lists(build_the_generator(parsed_args.apistorage_root, 'AccessionRecord'),
                                                    build_the_generator(parsed_args.apistorage_root, 'Collection'))

        for n_title in new_collection_titles:
            new_file_path = write_new_record(parsed_args.apistorage_root, n_title)
            if new_file_path:
                add_file_path_to_org_list(new_file_path, 'Collection')
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    main()
