from collections import namedtuple
from os.path import relpath
from sys import stderr

from pypremis.lib import PremisRecord

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a commmand line tool to run a fixity check run on the contents of longTermStorage"

def retrieve_accession_from_path(a_path, lts_root):
    """a function to extract the accession id from the path to a file from longTermStorage

    __Args__
    1. a_path (str): a longTermStorage path

    """
    path_str = relpath(a_path.path, lts_root)
    accession = path_str[0:path_str.index("arf")].replace('/','')
    return accession

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

