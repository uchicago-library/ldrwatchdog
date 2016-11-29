from collections import namedtuple
from os import scandir
from os.path import abspath, exists, join, relpath
import json
from sys import stderr

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord
from ldrpremisbuilding.utils import *
from pypremis.lib import PremisRecord

from .time_math import *

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a commmand line tool to run a fixity check run on the contents of longTermStorage"

def build_a_generator_of_premis_records(path, cache_file=None, lts_root=None):
    """a function to take a path and scan it recursively; building up a generator of premis records

    __Args__
    path (str): a path on the disk that this tool is running on.
    """
    for entry in scandir(path):
        if entry.is_dir():
            yield from build_a_generator_of_premis_records(entry.path, cache_file=cache_file, lts_root=lts_root)
        elif 'premis.xml' in entry.path and cache_file.get(retrieve_accession_from_path(entry, lts_root)) == None:
            yield entry

def build_a_generator_of_files_needing_fixity_check(path, live_premis_root=None):
    """a function to gather files to fixity check in this run based on evaluating the premis contents

    __Args__
    1. total_files (int)
    2. total_bytes (int)
    """
    for entry in scandir(path):
        if entry.is_dir():
            yield from build_a_generator(entry.path, live_premis_root=live_premis_root)
        if entry.is_file():
            premis_data = extract_identity_data_from_premis_record(entry.path)
            is_it_too_old = does_a_thing_need_to_be_checked_again(premis_data)
            if is_it_too_old and premis_data != None:
                arkid = entry.path[0:entry.path.index("arf")].split(live_premis_root)[1].replace('/','')
                package = namedtuple("file_to_check", "content_loc premis_path premis_record arkid objid fixity_value file_size")\
                                    (premis_data.content_loc, entry.path, premis_data.premis_record,
                                     arkid, premis_data.objid, premis_data.fixity_to_test, premis_data.file_size)
                yield package

def equality_check_two_strings(orig_hash, new_hash):
    """a function to compare two strings for equality

    __Args__
    1. left_string (str): a string, any string
    2. right_string (str): another string, any particular string, that needs to be checked
       if it is the same as the left_string
    """
    return orig_hash == new_hash

def does_a_thing_need_to_be_checked_again(premis_data):
    """a function to check if an event is a fixity event and whether that fixity
       is older than than prescribed age
    """
    date_evaluation = []
    for n_event in premis_data.events_list:
        if n_event[0] == 'fixity check':
            try:
                date_evaluation.append(is_an_event_past_due(n_event[1], 80))
            except:
                 date_evaluation.append(is_an_event_past_due(n_event[2], 80))
    if len(date_evaluation) == 0:
        return True
    elif True in date_evaluation:
        return True
    else:
        return False

def retrieve_accession_from_path(a_path, lts_root):
    """a function to extract the accession id from the path to a file from longTermStorage

    __Args__
    1. a_path (str): a longTermStorage path
    """
    path_str = relpath(a_path.path, lts_root)
    accession = path_str[0:path_str.index("arf")].replace('/','')
    return accession

def write_out_a_complete_file_tree(directory_string):
    """a function to write out a complete directory hierarchy to disk

    ___Args__
    1. directory_string (str): a string representing a path that needs to be written to disk
    """
    if abspath(directory_string) == directory_string:
        directory_string = directory_string[1:]
    new_output = "/"
    for n_part in directory_string.split("/"):
        new_output = join(new_output, n_part)
        if exists(new_output):
            pass
        else:
            makedirs(new_output, exist_ok=True)
    return True

def read_json_data(json_file_path):
    """a function to read data from a JSON file

    __Args__
    1. json_file_path (str): a path to a JSON file
    """
    data = None
    with open(json_file_path) as json_data:
        data = json.load(json_data)
    return data

