from os.path import basename, exists, join
from uuid import uuid4

from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

def get_path_to_records(root_path):
    return join(root_path, 'records')

def get_lines_from_org_file(org_file_path):
    if exists(org_file_path):
        return [x.strip() for x in open(org_file_path, 'r').readlines()]
    else:
        stderr.write("{} is not a valid apistorage category\n".format(category_name))

def get_collection_title(path_to_hierarchical_record):
    record = HierarchicalRecord(path_to_hierarchical_record)
    titles = record.get_field("Collection Title")
    if len(titles) == 1:
        return titles[0]
    else:
        stderr.write("There are too many collection titles for {}\n".format(path_to_hierarchical_record))

def select_org_file(path, category_name):
    return join(path, 'org', category_name)

def build_the_generator(path, category_name):
    lines = get_lines_from_org_file(select_org_file(path, category_name))
    for n_line in lines:
        yield get_collection_title(join(get_path_to_records(path), n_line))

def create_a_new_collection_record(a_title):
    new_record = HierarchicalRecord()
    new_record.add_to_field("Collection Title", a_title)
    jsonified_record = new_record.toJSON()
    return jsonified_record

def write_to_a_new_file(root_path, file_data):
    new_filename = join(get_path_to_records(root_path), 'collection'+uuid4().hex)
    if not exists(new_filename):
        with open(new_filename, "wb") as writing_file:
            writing_file.write(file_data.encode("utf-8"))
        return new_filename
    else:
        stderr.write("{} could not be written because it already exists.\n".format(new_filename))
        return None

def get_identifier(a_file_path):
    return basename(a_file_path)
