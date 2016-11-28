from collections import namedtuple
from os.path import exists, join, relpath
from sys import stderr

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord
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

def find_object_characteristics_from_premis(premis_object):
    return premis_object.get_objectCharacteristics()[0]

def find_fixities_from_premis(object_chars, digest_algo_filter):
    obj_fixiites = object_chars.get_fixity()
    for fixity in obj_fixiites:
        if fixity.get_messageDigestAlgorithm() == digest_algo_filter:
            return fixity.get_messageDigest()
    return None

def find_size_info_from_premis(object_chars):
    return object_chars.get_size()

def find_objid_from_premis(premis_object):
    return premis_object.get_objectIdentifier()[0].get_objectIdentifierValue()

def premis_data_packager(content_loc, this_record, objid, file_size, fixity_digest):
    return namedtuple("premis_data", "content_loc premis_record objid file_size fixity_to_test")\
                     (content_loc, this_record, objid, int(file_size), fixity_digest)

def extract_data_from_premis_record(premis_file):
    """a function to extract data needed to run a fixity check from a particular premis xml file
    __Args__
    1. premis_file (str or PremisRecord): a string pointing to a premis record on-disk or
    an instance of a PremisRecord
    """
    this_record = open_premis_record(premis_file)
    this_object = this_record.get_object_list()[0]
    the_characteristics = find_object_characteristics_from_premis(this_object)
    objid = find_objid_from_premis(this_object)
    file_size = find_size_info_from_premis(the_characteristics)
    fixity_digest = find_fixities_from_premis(the_characteristics, 'md5')
    content_loc = this_object.get_storage()[0].get_contentLocation().get_contentLocationValue()
    data = premis_data_packager(content_loc, this_record, objid, int(file_size), fixity_digest)
    print(data)
    return data

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


