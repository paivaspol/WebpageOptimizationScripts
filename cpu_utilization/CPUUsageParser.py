from argparse import ArgumentParser

import os

# Index constants
user_index = 2
nice_index = 3
system_index = 4
idle_index = 5
io_index = 6
irq_index = 7
soft_irq_index = 8
steal_index = 9
guest_index = 10
guest_nice_index = 11

def parse_file(filename, range_to_page_map, output_directory):
    result = dict()
    with open(filename, 'rb') as input_file:
        prev_line = input_file.readline().rstrip().split()
        cur_line = input_file.readline().rstrip().split()
        current_range_index = 0
        cur_page_range, cur_page_name = range_to_page_map[current_range_index]
        full_path = os.path.join(output_directory, cur_page_name)
        cur_file = open(full_path, 'wb')
        result[cur_page_name] = []
        while len(cur_line) != 0:
            current_time = int(cur_line[0])
            if current_time > cur_page_range[1]:
                # Out of range. Go to the next one.
                current_range_index += 1
                cur_file.close()
                if current_range_index >= len(range_to_page_map):
                    print 'here'
                    break
                cur_page_range, cur_page_name = range_to_page_map[current_range_index]
                full_path = os.path.join(output_directory, cur_page_name)
                cur_file = open(full_path, 'wb')
                result[cur_page_name] = []

            if cur_page_range[0] <= current_time <= cur_page_range[1]:
                prev_idle, prev_non_idle, prev_total = compute_stats_from_line(prev_line)
                cur_idle, cur_non_idle, cur_total = compute_stats_from_line(cur_line)
                idle_diff = cur_idle - prev_idle
                total_diff = cur_total - prev_total
                cpu_utilization = 1.0 * (total_diff - idle_diff) / total_diff
                remainder = (int(cur_line[0]) - cur_page_range[0]) % 100
                relative_time = (int(cur_line[0]) - cur_page_range[0]) - remainder
                cur_file.write(str(relative_time) + ' ' + str(cpu_utilization) + '\n')
                result[cur_page_name].append(cpu_utilization)
            prev_line = cur_line
            cur_line = input_file.readline().rstrip().split()
    print 'result: {0}'.format(result)
    return result

def compute_stats_from_line(line):
    idle = int(line[idle_index]) + int(line[io_index])
    
    user_time = int(line[user_index]) - int(line[guest_index])
    nice_time = int(line[nice_index]) - int(line[guest_nice_index])
    system_time = int(line[system_index])
    irq_time = int(line[irq_index])
    soft_irq_time = int(line[soft_irq_index])
    steal_time = int(line[steal_index])
    non_idle = user_time + nice_time + system_time + irq_time + soft_irq_time + steal_time
    
    total = idle + non_idle
    return idle, non_idle, total

def get_range_to_page_map(range_filename):
    result = dict()
    with open(range_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.rstrip().split()
            time_range = (int(line[1]), int(line[2]))
            page = line[0].replace('http://', '')
            result[time_range] = page
    sorted_result = sorted(result.items(), key=lambda x: x[0][0])
    return sorted_result

def output_utilizations_for_all_pages(page_cpu_utilization_map, output_dir):
    full_path = os.path.join(output_dir, 'page_cpu_utilization.txt')
    with open(full_path, 'wb') as output:
        for page, utilizations in page_cpu_utilization_map.iteritems():
            output.write(page)
            for utilization in utilizations:
                output.write(' ' + str(utilization))
            output.write('\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('log_filename')
    parser.add_argument('range_filename')
    parser.add_argument('output_directory')
    args = parser.parse_args()
    range_to_page_map = get_range_to_page_map(args.range_filename)
    utilization_for_all_pages = parse_file(args.log_filename, range_to_page_map, args.output_directory)
    output_utilizations_for_all_pages(utilization_for_all_pages, args.output_directory)
