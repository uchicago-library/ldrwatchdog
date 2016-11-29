from argparse import ArgumentParser
from os import makedirs, scandir
from os.path import dirname, exists, isdir, join, relpath, abspath

from sys import stdout, stderr

from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldrpath import LDRPath
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldritemcopier import LDRItemCopier

from ..lib.utils import build_a_generator_of_premis_records, read_json_data, retrieve_accession_from_path, write_out_a_complete_file_tree

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a command line tool to find all premis records in longTermStorage and if not already in livePremis copy the file into livePremis"

def iterate_over_premisrecords(cached_file, longterm, live_premis):
    """a function to iterate over premisreocrds
    __Args__
    cached_file (str): path to the livePremis cache file
    longterm (str): a string representing the root to the longTermStorage location on the disk
    live_premis (str): a string representing the root to the livePremis location on the disk
    """
    cache_data = read_json_data(cached_file)
    longterm_accessions = build_a_generator_of_premis_records(longterm, cache_file=cache_data, lts_root=longterm)
    tally = 0
    for n_entry in longterm_accessions:
        live_record_path = join(live_premis, n_entry.path.split('pairtree_root')[1])
        relative_path = relpath(n_entry.path, longterm)
        source_string = n_entry.path
        destination_string = join(live_premis, relative_path)
        check = source_string.split('/data/repository/longTermStorage')[1] == destination_string.split('/data/repository/livePremis')[1]
        source_path = LDRPath(source_string)
        destination_path = LDRPath(destination_string)
        tree_written = write_out_a_complete_file_tree(dirname(destination_string))
        if tree_written:
            copier = LDRItemCopier(source_path, destination_path, eq_detect="size")
            copy_report = copier.copy()
            if copy_report['src_eqs_dst']:
                new_cache_data[retrieve_accession_from_path(n_entry, longterm)] = {'completed':True}
            else:
                stderr.write("{} was not copied\n".format(n_entry.path))
        tally += 1
    stdout.write("{} new premis records added to {}\n".format(tally, live_premis))
    with open(cached_file, 'w') as write_file:
        json.dump(new_cache_data, write_file)

def main():
    """the main function of the command-line module
    """
    try:
        arguments = ArgumentParser(description="A tool to check for new premis records in longTermStorage",
                                   epilog="Copyright University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
        arguments.add_argument("longterm_root", action="store", help="the location of longTermStorage")
        arguments.add_argument("livepremis_root", action="store", help="the locaiton of livePremis")
        parsed_args = arguments.parse_args()
        cached_file = join(parsed_args.livepremis_root, "cached.json")
        iterate_over_premisrecords(cached_file, parsed_args.longterm_root, parsed_args.livepremis_root)
        return 0
    except KeyboardInterrupt:
        return 131

