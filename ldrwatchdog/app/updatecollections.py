from argparse import ArgumentParser
from os import scandir, _exit
from os.path import exists, join
from json.decoder import JSONDecodeError
from uuid import uuid4

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

__AUTHOR__ = "Tyler Danstrom"
__EMAIL__ = "tdanstrom@uchicago.edu"
__VERSION__ = "1.0.0"
__DESCRIPTION__ = "a module to use in a command line tool to find all premis records in longTermStorage and if not already in livePremis copy the file into livePremis"

def scantree_for_acc_records(path, name_filter):
   for n_entry in scandir(path):
        if name_filter and name_filter not in n_entry.path:
            try:
                yield HierarchicalRecord(n_entry.path)
            except JSONDecodeError:
                pass

def scantree_for_collection_records(path, name_filter):
   for n_entry in scandir(path):
        if name_filter and name_filter in n_entry.path:
            try:
                yield HierarchicalRecord(n_entry.path)
            except JSONDecodeError:
                pass



def main():
    arguments = ArgumentParser(description="A cli application to create new hierarchicalrecords for collections when necessary",
                               epilog="Copyright The University of Chicago, 2016; authored by Tyler Danstrom <tdanstrom@uchicago.edu>")
    arguments.add_argument("apistorage_records", action='store', type=str, help="The location of apistorage")
    arguments.add_argument("collection_record_prefix", action='store', type=str, help="The prefix for collection hierarchical records")
    parsed_args = arguments.parse_args()
    parsed_args = arguments.parse_args()
    try:
        acc_records_generator = scantree_for_acc_records(parsed_args.apistorage_records, parsed_args.collection_record_prefix)
        coll_records_generator = scantree_for_collection_records(parsed_args.apistorage_records, parsed_args.collection_record_prefix)
        accession_collections = []
        collection_collections = []
        collection_collections_filepaths = []
        for n_thing in acc_records_generator:
            try:
                accession_collections.append(n_thing.get_field("Collection Title")[0])
            except KeyError:
                pass
        for n_thing in coll_records_generator:
            collection_collections.append(n_thing.get_field("Collection Title")[0])
        new_collections = [x for x in accession_collections if x not in collection_collections]
        for n_new_collection in new_collections:
            new_hier_record = HierarchicalRecord()
            new_hier_record.add_to_field("Collection Title", n_new_collection)
            json_new_hier_record = new_hier_record.toJSON()
            new_collection_filename = join(parsed_args.apistorage_records, 'collection'+uuid4().hex)
            if exists(new_collection_filename):
                pass
            else:
                with open(new_collection_filename, "w") as writing_file:
                    writing_file.write(json_new_hier_record)
        return 0
    except KeyboardInterrupt:
        return 131

if __name__ == "__main__":
    _exit(main())
