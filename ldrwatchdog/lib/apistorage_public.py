from os.path import basename

from ..lib.apistorage_utils import *

def compare_title_lists(new_list, old_list):
    return [x for x in new_list if x not in old_list]

def build_the_generator(path, category_name):
    lines = get_lines_from_org_file(select_org_file(path, category_name))
    for n_line in lines:
        yield get_collection_title(join(path, 'records', n_line))

def write_new_record(root_path, a_title):
    data_to_write = create_a_new_collection_record(a_title)
    return write_to_a_new_file(root_path, data_to_write)

def add_file_path_to_org_list(new_file_path, category_name):
    relevant_org_file = select_org_file(new_file_path.split('record')[0], category_name)
    identifier = get_identifier(new_file_path)
    print(identifier)
    with open(relevant_org_file, "a") as writing_file:
        writing_file.write(identifier+"\n")

