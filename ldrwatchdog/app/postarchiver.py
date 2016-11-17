from argparse import ArgumentParser
from os import _exit, makedirs, scandir
from os.path import dirname, exists, isdir, join
import json 

from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldrpath import LDRPath
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldritemcopier import LDRItemCopier

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a command line tool to find all premis records in longTermStorage and if not already in livePremis copy the file into livePremis"


def scantree(path, cache_file=None):
    """a function to take a path and scan it recursively; building up a generator of premis records

    __Args__
    path (str): a path on the disk that this tool is running on.
    """
    for entry in scandir(path):
        if entry.is_dir():
            yield from scantree(entry.path, cache_file=cache_file)
        elif 'premis.xml' in entry.path and cache_file.get(entry.path) == None:
            yield entry

def main(cached_file, longterm, live_premis):
    """the main function of the command-line module

    __Args__
    longterm (str): a string representing the root to the longTermStorage location on the disk
    live_premis (str): a string representing the root to the livePremis location on the disk
    """
    with open(cached_file) as json_data:
        cache_data = json.load(json_data)
    new_cache_data = cache_data
    try:
        longterm_accessions = scantree(longterm, cache_file=cache_data)
        for n in longterm_accessions:
            live_record_path = join(live_premis, n.path.split('pairtree_root')[1])
            relative_path = n.path.split("/data/repository/longTermStorage")[1]
            source_string = n.path
            destination_string = live_premis + relative_path
            makedirs(dirname(destination_string), exist_ok=True)
            source_path = LDRPath(source_string)
            destination_path = LDRPath(destination_string)
            copier = LDRItemCopier(source_path, destination_path, eq_detect="name")
            copier.copy()
            new_cache_data[source_string] = True
        with open(cached_file, 'w') as write_file:
            json.dump(new_cache_data, write_file)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    arguments = ArgumentParser(description="A tool to check for new premis records in longTermStorage",
                               epilog="Copyright University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
    arguments.add_argument("longterm_root", action="store", help="the location of longTermStorage")
    arguments.add_argument("livepremis_root", action="store", help="the locaiton of livePremis")
    parsed_args = arguments.parse_args()
    cached_file = join(parsed_args.livepremis_root, "cached.json")
    main(cached_file, parsed_args.longterm_root, parsed_args.livepremis_root)
