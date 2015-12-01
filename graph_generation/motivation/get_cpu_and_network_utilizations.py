from argparse import ArgumentParser

import subprocess

def main(pcap_filename, cpu_trace_filename, interval_filename, output_directory):
    cpu_utilization_cmd = 'python ~/Documents/research/MobileWebPageOptimization/scripts/cpu_utilization/find_cpu_utilization.py {0} {1} {2}'.format(cpu_trace_filename, interval_filename, output_directory)
    network_utilization_cmd = 'python ~/Documents/research/MobileWebPageOptimization/scripts/network_utilization/bandwidth_calculator.py {0} {1} {2}'.format(pcap_filename, interval_filename, output_directory)
    subprocess.call(cpu_utilization_cmd, shell=True)
    subprocess.call(network_utilization_cmd, shell=True)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_filename')
    parser.add_argument('cpu_trace_filename')
    parser.add_argument('interval_filename')
    parser.add_argument('output_directory')
    args = parser.parse_args()
    main(args.pcap_filename, args.cpu_trace_filename, args.interval_filename, args.output_directory)
