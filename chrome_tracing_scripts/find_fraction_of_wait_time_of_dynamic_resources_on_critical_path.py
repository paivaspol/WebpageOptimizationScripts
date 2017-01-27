import os, sys, json, numpy

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
            curr_path.append(child)
            find_path(child, curr_path, root_to_leaf_paths, object_mappings)

def compute(dep_tree, timing, dependencies):
    results = {}
    try:
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
        with open(timing) as f:
            for line in f:
                line = line.strip("\n")
                parts = line.split(" ")
                if parts[0] not in timings:
                    timings[parts[0]] = [int(parts[1]), int(parts[2]), int(parts[3])]
        # first find root
        root = ''
        root_to_leaf_paths = []
        for key in object_mappings:
            if object_mappings[key]['isRoot'] == True:
                root = key
        find_path(root, [root], root_to_leaf_paths, object_mappings)
        
        # for each path, compute network delays, finish time, and last_response-first_request
        max_delay = -1
        critical_path = []
        max_finish_time = -1
        critical_path_time = -1
        critical_path_dynamic_resource_network_delay = -1
        for path in root_to_leaf_paths:
            network_delay = 0
            finish_time = -1
            dynamic_resource_delay = 0
            for node in path:
                if ( node in timings ):
                    network_delay += (timings[node][2] - timings[node][0])
                    finish_time = max(finish_time, timings[node][2])
                    if node not in dependencies:
                        dynamic_resource_delay += (timings[node][2] - timings[node][0])

            if critical_path_time < finish_time:
                critical_path_time = network_delay
                critical_path = path
                critical_path_dynamic_resource_network_delay = dynamic_resource_delay

        fraction = 1.0 * critical_path_dynamic_resource_network_delay / critical_path_time
        return critical_path, critical_path_time, critical_path_dynamic_resource_network_delay, fraction
    except Exception as e:
        print e
        pass

def get_dependencies(dependency_filename):
    result = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.add(line[2])
    return result

dependencies = get_dependencies(dependency_filename)
critical_path, critical_path_time, critical_path_dynamic_resource_network_delay, fraction = compute(dep_tree, timing, dependencies)
print '{0} {1} {2}'.format(critical_path_dynamic_resource_network_delay, critical_path_time, fraction)
print critical_path
