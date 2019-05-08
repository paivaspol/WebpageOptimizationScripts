import os, sys, json, numpy

if len(sys.argv) < 3:
    print 'usage: [dep_tree] [timing] [node]'
    sys.exit(1)

dep_tree = sys.argv[1]
timing = sys.argv[2]
node = sys.argv[3]


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

def compute(dep_tree, timing, node):
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
        for path in root_to_leaf_paths:
            # pick the pack with the node as the last one
            if ( path[-1] != node ):
                continue
            if ( path[-1] in timings ):
                finish_time = timings[path[-1]][2]
            else:
                print "node is not listed in timings file!"
                exit()
            network_delay = 0
            for node in path:
                if ( node in timings ):
                    network_delay += (timings[node][2] - timings[node][0])
            print "PATH: " + str(path)
            print "Total network delay: " + str(network_delay)
            for obj in path:
                if ( obj in timings ):
                    print "OBJ: " + str(obj) + " has timings: " + str(timings[obj])
                else:
                    print "NO TIMING INFO FOR: " + obj
            break
    except Exception as e:
        print e
        pass
compute(dep_tree, timing, node)
