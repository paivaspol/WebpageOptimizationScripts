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

def parse_file(filename, output_directory):
    with open(filename, 'rb') as input_file:
        prev_line = input_file.readline().rstrip().split()
        cur_line = input_file.readline().rstrip().split()
        initial_time = int(prev_line[0])
        full_path = os.path.join(output_directory, 'result_all_pages.txt')
        # cur_file = open(full_path, 'wb')
        while len(cur_line) != 0:
            current_time = int(cur_line[0])
            prev_idle, prev_non_idle, prev_total = compute_stats_from_line(prev_line)
            cur_idle, cur_non_idle, cur_total = compute_stats_from_line(cur_line)
            idle_diff = cur_idle - prev_idle
            total_diff = cur_total - prev_total
            cpu_utilization = 1.0 * (total_diff - idle_diff) / total_diff
            relative_time = (int(cur_line[0]) - initial_time)
            # cur_file.write(str(relative_time) + ' ' + str(cpu_utilization) + '\n')
            print '{0} {1}'.format(relative_time, cpu_utilization)
            prev_line = cur_line
            cur_line = input_file.readline().rstrip().split()

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

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('log_filename')
    parser.add_argument('output_directory')
    args = parser.parse_args()
    parse_file(args.log_filename, args.output_directory)
