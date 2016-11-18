
from argparse import ArgumentParser
from collections import namedtuple
from datetime import datetime
from os import _exit, scandir
from uuid import uuid4

from pypremis.lib import PremisRecord
from pypremis.nodes import *
from uchicagoldrtoolsuite.core.lib.convenience import sane_hash
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldrpath import LDRPath

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a command line tool to run a fixity check run on the contents of longTermStorage"

LIVE_PREMIS = "/data/repository/livePremis"

def scantree(path, cache_file=None, lts_root=None):
    """a function to take a path and scan it recursively; building up a generator of premis records

    __Args__
    path (str): a path on the disk that this tool is running on.
    """
    for entry in scandir(path):
        if entry.is_dir():
            yield from scantree(entry.path, cache_file=cache_file, lts_root=lts_root)
        elif 'premis.xml' in entry.path and cache_file.get(retrieve_accession_from_path(entry, lts_root)) == None:
            yield entry

def gather_files(path):
    """a function to gather files to fixity check in this run based on evaluating the premis contents

    __Args__
    1. total_files (int)
    2. total_bytes (int)
    """
    for entry in scandir(path):
        if entry.is_dir():
            yield from gather_files(entry.path)
        if entry.is_file():
            this_record = PremisRecord(frompath=entry.path)
            this_object = this_record.get_object_list()[0]
            objid = this_object.get_objectIdentifier()[0].get_objectIdentifierValue()
            obj_fixiites = this_object.get_objectCharacteristics()[0].get_fixity()
            file_size = this_object.get_objectCharacteristics()[0].get_size()
            for fixity in obj_fixiites:
                if fixity.get_messageDigestAlgorithm() == 'md5':
                    fixity_to_test = fixity.get_messageDigest()
            content_loc = this_object.get_storage()[0].get_contentLocation().get_contentLocationValue()
            n_input = namedtuple("file_to_check", "content_loc premis_path objid fixity_value file_size")(content_loc, entry.path, objid, fixity_to_test, file_size)
            yield n_input

def main(total_allowed_files, total_allowed_bytes):
    """the main function of the command-line module

    __Args__
    total_allowed_files (int): an integer representing the total number of files that can be evaluated in this run
    total_allowed_bytes (int): an integer representing the total number of bytes that can be read in this run
    """
    try:
        files_to_check = gather_files(LIVE_PREMIS)
        bytes_read = 0
        files_used = 0
        for n in files_to_check:
            new_hash = sane_hash('md5', n.content_loc)
            event_id = EventIdentifier("DOI", str(uuid4()))
            linkedObject = LinkingObjectIdentifier("DOI", n.objid)
            linkedAgent = LinkingAgentIdentifier("DOI", str(uuid4()))
            if new_hash == n.fixity_value:
                print(n.premis_path)
                event_outcome = EventOutcomeInformation("success", "ldrwatchdog.fixitychecker performed fixity check and passed")
            else:
                event_outcome = EventOutcomeInformation("failure", "ldrwatchdog.fixitychecker performed fixity check and it failed")
            new_event = Event(event_id, "fixity check", datetime.now().isoformat().split('T')[0])
            new_event.set_linkingAgentIdentifier(linkedAgent)
            new_event.set_eventOutcomeInformation(event_outcome)
            new_event.set_linkingObjectIdentifier(linkedObject)
            this_record = PremisRecord(frompath=n.premis_path)
            this_record.add_event(new_event)
            this_record.write_to_file(n.premis_path)
            bytes_read += int(n.file_size)
            files_used += 1
            if bytes_read >= total_allowed_bytes or files_used >= total_allowed_files:
                break
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    arguments = ArgumentParser(description="a command-line tool to check fixity of files in longTermStorage",
                               epilog="Copyright University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
    arguments.add_argument("max_num_files", action='store', type=int, help="maximum allowed number of files for this run")
    arguments.add_argument("-b", "--max_bytes_to_read", action='store', type=int, help="total number of bytes to read for this run")
    parsed_args = arguments.parse_args()
    _exit(main(parsed_args.max_num_files, parsed_args.max_bytes_to_read))
