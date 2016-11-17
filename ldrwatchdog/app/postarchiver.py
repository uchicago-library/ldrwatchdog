from argparse import ArgumentParser
from os import _exit, scandir
from os.path import exists, isdir, join

from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldrpath import LDRPath
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldritemcopier import LDRItemCopier

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a command line tool to find all premis records in longTermStorage and if not already in livePremis copy the file into livePremis"

def scantree(path):
    for entry in scandir(path):
        if entry.is_dir():
            yield from scantree(entry.path)
        elif 'premis.xml' in entry.path:
            yield entry

def main(longterm, live_premis):
    try:
        longterm_accessions = scantree(longterm)
        for n in longterm_accessions:
            live_record_path = live_premis + n.path.split('pairtree_root')[1]
            if not exists(live_record_path):
                relative_path = n.path.split("/data/repository/longTermStorage")[1]
                source_string = n.path
                destination_string = live_premis + relative_path
                source_path = LDRPath(source_string)
                destination_path = LDRPath(destination_string)
                copier = LDRItemCopier(source_path, destination_path, eq_detect="name")
                copier.copy()
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    arguments = ArgumentParser(description="A tool to check for new premis records in longTermStorage",
                               epilog="Copyright University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
    arguments.add_argument("longterm_root", action="store", help="the location of longTermStorage")
    arguments.add_argument("livepremis_root", action="store", help="the locaiton of livePremis")
    parsed_args = arguments.parse_args()
    main(parsed_args.longterm_root, parsed_args.livepremis_root)
