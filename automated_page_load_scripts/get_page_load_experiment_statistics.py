import sys
import numpy

filename = sys.argv[1]  # Get the filename

page_load_dictionary = dict() # The dictionary from the page to a list of page load time.
current_page = None
with open(filename, 'rb') as input_file:
    for raw_line in input_file:
        line = raw_line.strip()
        if line.startswith('Page: '):
            line = line.split()
            if line[1] not in page_load_dictionary:
                page_load_dictionary[line[1]] = []
                current_page = line[1]
        else:
            load_time = int(line)
            page_load_dictionary[current_page].append(load_time)
    
    for page in page_load_dictionary:
        load_times = page_load_dictionary[page]
        median = numpy.median(load_times)
        average = numpy.average(load_times)
        stdev = numpy.std(load_times)
        print 'Page: {0}'.format(page)
        print 'Median: {0}'.format(median)
        print 'Average: {0}'.format(average)
        print 'Stdev: {0}'.format(stdev)
        print ''

