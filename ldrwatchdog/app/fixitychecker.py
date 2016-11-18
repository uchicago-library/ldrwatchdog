
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

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a commmand line tool to run a fixity check run on the contents of longTermStorage"

LIVE_PREMIS = "/data/repository/livePremis"

def find_particular_event(event_list, event_string):
    output = None
    for n_event in event_list:
        if n_event.get_eventCategory() == event_string:
            output = n_event
            break
    return output

def get_events_from_a_premis_record(premis_record):
    """a function to retrieve a list of events from a given premis record

    __Args__
    1, premis_record (PremisRecord):
    """
    if not isinstance(premis_record, PremisRecord):
        raise ValueError("{} is not a valid PremisRecord instance\n".format(str(premis_record)))
    events = premis_record.get_events()
    return events

def open_premis_record(premis_file_path):
    """a function to attempt to create an instance of a PremisRecord

    __Args__
    1. premis_file_path (str): a string pointing to the location of a premis xml file on-disk
    """
    output = None
    try:
        output = PremisRecord(frompath=premis_file_path)
    except ValueError:
        stderr.write("{} is not a valid premis record\n".format(premis_file_path))
    return output

def compare_two_hashes(orig_hash, new_hash):
    return orig_hash == new_hash

def extract_data_from_premis_record(premis_file, is_premis_object=False):
    """a function to extract data needed to run a fixity check from a particular premis xml file

    __Args__
    1. premis_file (str or PremisRecord): a string pointing to a premis record on-disk or
    an instance of a PremisRecord
    """
    if is_premis_object:
        this_record = premis_file
    else:
        this_record = open_premis_record(premis_file)
    if this_record:
        this_object = this_record.get_object_list()[0]
        objid = this_object.get_objectIdentifier()[0].get_objectIdentifierValue()
        file_size = this_object.get_objectCharacteristics()[0].get_size()
        obj_fixiites = this_object.get_objectCharacteristics()[0].get_fixity()
        content_loc = this_object.get_storage()[0].get_contentLocation().get_contentLocationValue()
        for fixity in obj_fixiites:
            if fixity.get_messageDigestAlgorithm() == 'md5':
                fixity_to_test = fixity.get_messageDigest()
        return namedtuple("premis_data", "content_loc premis_record objid file_size fixity_to_test")\
                         (content_loc, this_record, objid, int(file_size), fixity_to_test)
    else:
        return None

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
                arkid = entry.path[0:entry.path.index("arf")].split(LIVE_PREMIS)[1].replace('/','')
                if event_date_delta:
                    if event_date_delta < current_date or len(fixity_check_dates) == 0:
                        n_input = namedtuple("file_to_check", "content_loc premis_path premis_record arkid objid fixity_value file_size")(premis_data.content_loc, entry.path, premis_data.premis_record, arkid, premis_data.objid, premis_data.fixity_to_test, premis_data.file_size)
                        yield n_input
                else:
                    n_input = namedtuple("file_to_check", "content_loc premis_path premis_record arkid objid fixity_value file_size")(premis_data.content_loc, entry.path, premis_data.premis_record, arkid, premis_data.objid, premis_data.fixity_to_test, premis_data.file_size)
                    yield n_input
            else:
                stderr.write("could not open {}\n".format(entry.path))

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
