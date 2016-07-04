import os

def get_pages_without_pages_to_ignore(base_pages, pages_to_ignore_filename):
    pages_to_ignore = set()
    with open(pages_to_ignore_filename, 'rb') as input_file:
        for raw_line in input_file:
            pages_to_ignore.add(raw_line.strip())
    base_pages_set = set(base_pages)
    return base_pages_set - pages_to_ignore

def setup_directory(output_dir, page):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if not os.path.exists(os.path.join(output_dir, page)):
        os.mkdir(os.path.join(output_dir, page))

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory
