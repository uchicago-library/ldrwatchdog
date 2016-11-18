from os import makedirs, scandir
from os.path import dirname, exists, isdir, join, relpath
import json 

from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldrpath import LDRPath
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldritemcopier import LDRItemCopier

from ..lib.utils import retrieve_accession_from_path

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a command line tool to find all premis records in longTermStorage and if not already in livePremis copy the file into livePremis"

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
        longterm_accessions = scantree(longterm, cache_file=cache_data, lts_root=longterm)
        for n_entry in longterm_accessions:
            live_record_path = join(live_premis, n_entry.path.split('pairtree_root')[1])
            relative_path = relpath(n_entry.path, longterm)
            source_string = n_entry.path
            destination_string = join(live_premis, relative_path)
            makedirs(dirname(destination_string), exist_ok=True)
            source_path = LDRPath(source_string)
            destination_path = LDRPath(destination_string)
            copier = LDRItemCopier(source_path, destination_path, eq_detect="name")
            copier.copy()
            new_cache_data[retrieve_accession_from_path(n_entry, longterm)] = True
            stdout.write("{}\n".format(n_entry))
        with open(cached_file, 'w') as write_file:
            json.dump(new_cache_data, write_file)
        return 0
    except KeyboardInterrupt:
        return 131


