from argparse import ArgumentParser
from collections import namedtuple
from datetime import datetime, timedelta

from sys import stderr, stdout
from time import mktime, strptime
from uuid import uuid4

from ldrpremisbuilding.utils import *
from pypremis.lib import PremisRecord
from pypremis.nodes import *
from uchicagoldrtoolsuite.core.lib.convenience import sane_hash
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldrpath import LDRPath

from ..lib.utils import *
from ..lib.time_math import *

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a commmand line tool to run a fixity check run on the contents of longTermStorage"

def iterate_over_files(livepremis_loc, total_allowed_files, total_allowed_bytes, hash_algo=None):
    """the main function of the command-line module

    __Args__
    total_allowed_files (int): an integer representing the total number of files that can be evaluated in this run
    total_allowed_bytes (int): an integer representing the total number of bytes that can be read in this run
    """
    files_to_check = build_a_generator(livepremis_loc,live_premis_root=livepremis_loc)
    bytes_read = 0
    files_used = 0
    hash_algo = hash_algo if hash_algo else "md5"
    for n_file_data in files_to_check:
        rederived_hash = sane_hash(hash_algo, n_file_data.content_loc)
        comparison_result = equality_check_two_strings(rederived_hash, n_file_data.fixity_value)
        if comparison_result:
            fixity_event = build_fixity_premis_event("fixity check",
                                                     datetime.now().isoformat(),
                                                     "SUCCESS",
                                                     "ldrwatchdog.fixitycheck was run with hash algorithm {} and it passed ".\
                                                     format(hash_algo),
                                                     n_file_data.objid,
                                                     "ldrwatchdog.fixitycheck")
        else:
            stderr.write("{} has fixity value {} now but it had {} on ingest.\n".format(join(n_file_data.arkid,
                                                                                             n_file_data.objid),
                                                                                             rederived_hash,
                                                                                             n_file_data.fixitiy_value))
            fixity_event = build_fixity_premis_event("fixity check",
                                                     datetime.now().isoformat(),
                                                     "FAILURE",
                                                     "ldrwatchdog.fixitycheck was run with hash algorithm {} and it failed ".\
                                                     format(hash_algo),
                                                     n_file_data.objid,
                                                     "ldrwatchdog.fixitycheck")
        add_event_to_a_premis_record(n_file_data.premis_record, fixity_event)
        write_a_premis_record(n_file_data.premis_record, n_file_data.premis_path)
        bytes_read += int(n_file_data.file_size)
        files_used += 1
        if total_allowed_bytes and bytes_read >= total_allowed_bytes:
            break
        elif files_used >= total_allowed_files:
            break

def main():
    try:
        arguments = ArgumentParser(description="a command-line tool to check fixity of files in longTermStorage",
                                   epilog="Copyright University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
        arguments.add_argument("livePremis", action='store', help="location on-disk of livePremis directory")
        arguments.add_argument("max_num_files", action='store', type=int, help="maximum allowed number of files for this run")
        arguments.add_argument("-b", "--max_bytes_to_read", action='store', type=int, help="total number of bytes to read for this run")
        arguments.add_argument("--hash-algo", action='store', type=str, choices=['crc32', 'sha256', 'adle32'], help="the default hash algorithm is md5")
        parsed_args = arguments.parse_args()
        iterate_over_files(parsed_args.livePremis, parsed_args.max_num_files, parsed_args.max_bytes_to_read, hash_algo=parsed_args.hash_algo)
        return 0
    except KeyboardInterrupt:
        return 131
