import os, sys, json, numpy

import constants

if len(sys.argv) < 3:
    print 'usage: [dep_tree] [timing] [dependency_filename]'
    sys.exit(1)

dep_tree = sys.argv[1]
timing = sys.argv[2]
dependency_filename = sys.argv[3]

# iterate through the dependency graph and make a list of all root-to-leaf paths
def find_path(start, path, root_to_leaf_paths, object_mappings):
    if ( object_mappings[start]['isLeaf'] == True ): # finishes the path
        root_to_leaf_paths.append(path)
    else:
        children = object_mappings[start]['children']
        for child in children:
            curr_path = list(path)
            if child not in curr_path:
                curr_path.append(child)
                try:
                    find_path(child, curr_path, root_to_leaf_paths, object_mappings)
                except Exception as e:
                    pass

def parse_timings(timing_filename):
    result = dict()
    with open(timing_filename, 'rb') as input_file:
        for line in input_file:
            line = line.strip()
            timing = json.loads(line)
            result[timing[constants.URL]] = timing
    return result

def compute(dep_tree, timing, dependencies):
    results = {}
    object_mappings = {}
    # read in the JSON file for the dependency graph
    total = ''
    with open(dep_tree) as f:
        for line in f:
            total += line
    object_mappings = json.loads(total)
    
    # keys are urls, values are arrays with [request_time, first_byte, last_byte]
    timings = {}
    # read in timing info
    timings = parse_timings(timing)

    # first find root
    root = ''
    root_to_leaf_paths = []
    for key in object_mappings:
        if object_mappings[key]['isRoot'] == True:
            root = key
    find_path(root, [root], root_to_leaf_paths, object_mappings)
    
    # for each path, compute network delays, finish time, and last_response-first_request
    critical_path = []
    critical_path_time = -1
    critical_path_net_delay = -1
    for path in root_to_leaf_paths:
        dynamic_resource_network_delay = 0
        finish_time = -1
        num_dynamic_resources = 0
        net_delay = 0
        for node in path:
            if ( node in timings ):
                # Network delay is defined as the time when the resource is discovered via 
                # parser / execution until the loading of the resource is completed.
                # If the resource finish downloading before the parser discovers the resource,
                # assume that that is 0.
                #
                # network_delay = max(0, timings.finish_time - timings.preload_discovery_time)
                #
                # If the object wasn't preloaded, then the time would be send request --> finish time
                if timings[node][constants.TRACING_PRELOADED]:
                    tmp_net_delay = timings[node][constants.TRACING_NETWORK_RESOURCE_FINISH] - timings[node][constants.TRACING_NETWORK_PRELOAD_DISCOVERY_TIME]
                else:
                    tmp_net_delay = timings[node][constants.TRACING_NETWORK_RESOURCE_FINISH] - timings[node][constants.TRACING_NETWORK_RESOURCE_SEND_REQUEST]

                net_delay += tmp_net_delay
                if node not in dependencies:
                    dynamic_resource_network_delay += max(0, tmp_net_delay)
                    num_dynamic_resources += 1

                if len(timings[node][constants.TRACING_PROCESSING_TIME]) > 0:
                    end_time = timings[node][constants.TRACING_PROCESSING_TIME][1]
                else:
                    end_time = timings[node][constants.TRACING_NETWORK_RESOURCE_FINISH]
                finish_time = max(finish_time, end_time)

        if critical_path_time < finish_time:
            critical_path_time = finish_time
            critical_path = path
            critical_path_net_delay = net_delay
            critical_path_not_hinted = num_dynamic_resources
            critical_path_dynamic_wait_time = dynamic_resource_network_delay

    return critical_path, critical_path_time, critical_path_not_hinted, critical_path_dynamic_wait_time, critical_path_net_delay

def get_dependencies(dependency_filename):
    result = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            if not raw_line.startswith("about:blank"):
                result.add(line[2])
    return result

dependencies = get_dependencies(dependency_filename)
critical_path, critical_path_time, critical_path_not_hinted, critical_path_dynamic_wait_time, critical_path_net_delay = compute(dep_tree, timing, dependencies)
print 'critical path:'
print critical_path
fraction = 1.0 * critical_path_dynamic_wait_time / critical_path_time
print '{0} {1} {2}'.format(critical_path_dynamic_wait_time, critical_path_time, fraction)
fraction_dynamic_resources = 1.0 * critical_path_not_hinted / len(critical_path)
print 'fraction not hinted: {0}'.format(fraction_dynamic_resources)
fraction_critical_path_net_delay = 1.0 * critical_path_dynamic_wait_time / critical_path_net_delay
print 'fraction critical path net delay: {0}'.format(fraction_critical_path_net_delay)
