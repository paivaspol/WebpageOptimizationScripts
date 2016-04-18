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

def parse_file(filename, interval, output_files):
    result = dict() # cpu, cpu0, cpu1, ...
    with open(filename, 'rb') as input_file: 
        prev_time, prev_line = get_next_time(input_file)
        while prev_time < interval[0]:
            # Not in the interval yet. Skip these lines.
            prev_time, prev_line = get_next_time(input_file)
        current_time, cur_line = get_next_time(input_file)
        initial_time = prev_time
        # full_path = os.path.join(output_directory, 'result_all_pages.txt')
        while len(cur_line) != 0:
            for i in range(0, len(prev_line)):
                prev_idle, prev_non_idle, prev_total = compute_stats_from_line(prev_line[i])
                cur_idle, cur_non_idle, cur_total = compute_stats_from_line(cur_line[i])
                idle_diff = cur_idle - prev_idle
                total_diff = cur_total - prev_total
                cpu_utilization = 1.0 * (total_diff - idle_diff) / total_diff
                relative_time = (current_time - initial_time)
                output_files[i].write('{0} {1}\n'.format(relative_time, cpu_utilization))
            prev_line = cur_line
            current_time, cur_line = get_next_time(input_file)
            if current_time > interval[1]:
                # Out of the interval. Stop the loop.
                break

def get_next_time(input_file):
    '''
    Returns the data of the next timestamp
    '''
    proc_result = []
    for i in range(0, 5):
        split_line = input_file.readline().strip().split()
        if len(split_line) == 0:
            return -1, []
        proc_result.append(split_line)
    return int(proc_result[0][0]), proc_result

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

def parse_interval(interval_filename):
    '''
    Parses the interval file.
    '''
    with open(interval_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return line[0], (int(line[1]), int(line[2]))

def open_output_files(output_directory, target_cpu=None):
    result = []
    for i in range(0, 5):
        if target_cpu is not None:
            filename = 'cpu_{0}_usage.txt'.format(target_cpu)
        else:
            if i == 0:
                filename = 'average_cpu_usage.txt'
            else:
                filename = 'cpu_{0}_usage.txt'.format(i - 1)
        output_filename = os.path.join(output_directory, filename)
        result.append(open(output_filename, 'wb'))
    return result

def close_output_files(output_files):
    for output_file in output_files:
        output_file.close()

def parse_target_cpu_file(target_cpu_filename):
    with open(target_cpu_filename, 'rb') as input_file:
        return int(input_file.readline().strip())

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('log_filename')
    parser.add_argument('interval_filename')
    parser.add_argument('output_directory')
    parser.add_argument('--target-cpu', default=None)
    args = parser.parse_args()
    if args.target_cpu is not None:
        target_cpu = parse_target_cpu_file(args.target_cpu)
    _, interval = parse_interval(args.interval_filename)
    output_files = open_output_files(args.output_directory)
    parse_file(args.log_filename, interval, output_files)
