def parse_page_start_end_time(page_start_end_time_filename):
    '''
    Parses the page start and end time and returns a list of tuples in the following format:
        ('page', ([start], [end]))
    '''
    result = []
    with open(page_start_end_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.append((line[0], (int(line[1]), int(line[2]))))
    return result
