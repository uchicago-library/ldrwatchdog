from collections import namedtuple
from datetime import datetime, timedelta
from os import scandir
from sys import stderr
from time import mktime, strptime
from uuid import uuid4

from pypremis.lib import PremisRecord
from pypremis.nodes import *
from uchicagoldrtoolsuite.core.lib.convenience import sane_hash
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldrpath import LDRPath

from ..lib.utils import find_particular_event, get_events_from_a_premis_record, extract_data_from_premis_record, open_premis_record

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a commmand line tool to run a fixity check run on the contents of longTermStorage"

def compare_two_hashes(orig_hash, new_hash):
    return orig_hash == new_hash

def gather_files(path, live_premis_root=None):
    """a function to gather files to fixity check in this run based on evaluating the premis contents

    __Args__
    1. total_files (int)
    2. total_bytes (int)
    """
    for entry in scandir(path):
        if entry.is_dir():
            yield from gather_files(entry.path, live_premis_root=live_premis_root)
        if entry.is_file():
            premis_data = extract_data_from_premis_record(entry.path)
            if premis_data:
                event_list = premis_data.premis_record.get_event_list()
                fixity_check_dates = []
                for n_event in event_list:
                    event_type =  n_event.get_eventType()
                    if event_type == "fixity check":
                        fixity_check_dates.append(n_event.get_eventDateTime())
                current_date = datetime.now() - timedelta(days=80)
                event_date_delta = None
                for n_fixity_date in fixity_check_dates:
                    try:
                        event_date_delta = strptime(n_fixity_date, "%Y-%m-%d")
                    except ValueError:
                        event_date_delta = strptime(n_fixity_date.split('T')[0], "%Y-%m-%d")
                    event_date_delta = datetime.fromtimestamp(mktime(event_date_delta))
                arkid = entry.path[0:entry.path.index("arf")].split(live_premis_root)[1].replace('/','')
                if event_date_delta:
                    if event_date_delta < current_date or len(fixity_check_dates) == 0:
                        n_input = namedtuple("file_to_check", "content_loc premis_path premis_record arkid objid fixity_value file_size")(premis_data.content_loc, entry.path, premis_data.premis_record, arkid, premis_data.objid, premis_data.fixity_to_test, premis_data.file_size)
                        yield n_input
                else:
                    n_input = namedtuple("file_to_check", "content_loc premis_path premis_record arkid objid fixity_value file_size")(premis_data.content_loc, entry.path, premis_data.premis_record, arkid, premis_data.objid, premis_data.fixity_to_test, premis_data.file_size)
                    yield n_input
            else:
                stderr.write("could not open {}\n".format(entry.path))

def main(livepremis_loc, total_allowed_files, total_allowed_bytes):
    """the main function of the command-line module

    __Args__
    total_allowed_files (int): an integer representing the total number of files that can be evaluated in this run
    total_allowed_bytes (int): an integer representing the total number of bytes that can be read in this run
    """
    try:
        files_to_check = gather_files(livepremis_loc,live_premis_root=livepremis_loc)
        bytes_read = 0
        files_used = 0
        checked = []
        for n in files_to_check:
            new_hash = sane_hash('md5', n.content_loc)
            event_id = EventIdentifier("DOI", str(uuid4()))
            linkedObject = LinkingObjectIdentifier("DOI", n.objid)
            linkedAgent = LinkingAgentIdentifier("DOI", str(uuid4()))
            if new_hash == n.fixity_value:
                event_result = "success"
                event_message = "ldrwatchdog.fixitychecker performed fixity check and passed"
            else:
                event_result = "failure"
                event_message = "ldrwatchdog.fixitychecker performed fixity check and it failed"
                stderr.write("{}/{} content file failed fixity check".format(n.arkid, n.objid))
            event_detail = EventOutcomeDetail(eventOutcomeDetailNote=event_message)
            event_outcome = EventOutcomeInformation(event_result, event_detail)
            new_event = Event(event_id, "fixity check", datetime.now().isoformat())
            new_event.set_linkingAgentIdentifier(linkedAgent)
            new_event.set_eventOutcomeInformation(event_outcome)
            new_event.set_linkingObjectIdentifier(linkedObject)
            this_record = n.premis_record
            this_record.add_event(new_event)
            this_record.write_to_file(n.premis_path)
            bytes_read += int(n.file_size)
            files_used += 1
            checked.append(n)
            if total_allowed_bytes and bytes_read >= total_allowed_bytes:
                break
            elif files_used >=  total_allowed_files:
                break
        return 0
    except KeyboardInterrupt:
        return 131
