def parse_page_start_end_time(page_start_end_time_filename):
    '''
    Parses the page start and end time and returns a list of tuples in the following format:
        ('page', ([start], [end]))
    '''
    result = []
    with open(page_start_end_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.append((line[0], (float(line[1]), float(line[2]))))
    if len(result) > 1:
        return result
    else:
        return result[0]

def extract_url_from_path(path):
    '''
    Extracts the url from the path.
    '''
    last_delim_index = -1
    for i in range(0, len(path)):
        if path[i] == '/':
            last_delim_index = i
    return path[last_delim_index + 1:]
