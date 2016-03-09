import simplejson as json
import common_module
import os

from argparse import ArgumentParser 

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
INITIATOR = 'initiator'
REQUEST = 'request'
RESPONSE = 'response'
REQUEST_HEADERS = 'requestHeaders'
REFERER = 'referer'
URL = 'url'
STACKTRACE = 'stackTrace'
TYPE = 'type'
TIMESTAMP = 'timestamp'

DEFAULT_REQUESTER = '##default'

def find_dependencies(network_activities, page_start_end_time):
    '''
    Finds the dependency of the resources
    The ordering of the initiator extraction is as follows:
        1) From the initiator field in Network.requestWillBeSent
        2) From referer in HTTP header in Network.responseReceived
        3) From DocumentURL in the Network.requestWillBeSent event
    '''
    request_id_to_initiator_map = dict() # Maps from the resource to initiator.
    request_id_to_resource_map = dict() # Maps from the request id to the resource url
    request_id_to_document_url = dict() # Maps from the request id to the document url.
    request_id_to_request_object = dict() # Maps from the request id to the network event.
    start_time, end_time = page_start_end_time[2]
    for network_activity in network_activities:
        if TIMESTAMP not in network_activity[PARAMS]:
            continue

        ts = common_module.convert_to_ms(network_activity[PARAMS][TIMESTAMP])
        if not start_time <= ts <= end_time:
            # If the event doesn't fall in the page load range.
            continue

        if METHOD in network_activity and \
            network_activity[METHOD] == 'Network.requestWillBeSent':
            # print REQUEST + ': ' + str(network_activity[PARAMS][REQUEST][URL])
            # print INITIATOR + ': ' + str(network_activity[PARAMS][INITIATOR]) + '\n'
            requester = None
            if network_activity[PARAMS][INITIATOR][TYPE] == 'script' and STACKTRACE in network_activity[PARAMS][INITIATOR]:
                call_stack = network_activity[PARAMS][INITIATOR][STACKTRACE]
                requester = call_stack[len(call_stack) - 1][URL]
            elif network_activity[PARAMS][INITIATOR][TYPE] == 'parser' and URL in network_activity[PARAMS][INITIATOR]:
                requester = network_activity[PARAMS][INITIATOR][URL]
            else:
                # Case where there isn't either URL or STACKTRACE
                 requester = DEFAULT_REQUESTER
            request_id = network_activity[PARAMS][REQUEST_ID]
            request_id_to_resource_map[request_id] = network_activity[PARAMS][REQUEST][URL]
            request_id_to_initiator_map[request_id] = requester
            request_id_to_document_url[request_id] = network_activity[PARAMS]['documentURL']
            request_id_to_request_object[request_id] = network_activity
        elif METHOD in network_activity and \
            network_activity[METHOD] == 'Network.responseReceived':
            request_id = network_activity[PARAMS][REQUEST_ID]
            if request_id not in request_id_to_request_object:
                continue
            request_network_activity = request_id_to_request_object[request_id]
            if request_id in request_id_to_initiator_map and \
                request_network_activity[PARAMS][INITIATOR][TYPE] == 'parser':
                # Try to apply the second extraction rule: use the referer instead.
                response = network_activity[PARAMS][RESPONSE]
                if REQUEST_HEADERS in response and REFERER in response[REQUEST_HEADERS] and \
                    response[REQUEST_HEADERS][REFERER].endswith('.css'):
                    request_id_to_initiator_map[request_id] = response[REQUEST_HEADERS][REFERER]
            elif request_id in request_id_to_document_url and \
                request_id_to_initiator_map[request_id] == DEFAULT_REQUESTER:
                # Try to apply the third extraction rule: use the DocumentURL
                request_id_to_initiator_map[request_id] = request_id_to_document_url[request_id]

    dep_tree = populate_dependencies(request_id_to_initiator_map, request_id_to_resource_map)
    return { key: dep_tree[key] for key in dep_tree if key != DEFAULT_REQUESTER }

def populate_dependencies(request_id_to_initiator_map, request_id_to_document_url):
    dep_tree = dict()
    for request_id, initiator in request_id_to_initiator_map.iteritems():
        if initiator not in dep_tree:
            dep_tree[initiator] = []
        document_url = request_id_to_document_url[request_id]
        dep_tree[initiator].append(document_url)
    return dep_tree

def convert_to_object(network_data_file):
    '''
    Converts from string representation of JSON to an object.
    '''
    network_activities = []
    with open(network_data_file, 'rb') as input_file:
        for raw_line in input_file:
            json_str = raw_line.strip()
            json_obj = json.loads(json_str)
            network_activities.append(json.loads(json_obj))
    return network_activities

def output_dep_graph(dep_graph, initiator, prefix):
    '''
    Outputs the dependency graph.
    '''
    if initiator in dep_graph:
        current_dependencies = dep_graph[initiator]
        for dependency in current_dependencies:
            print prefix + ' ' + dependency
            output_dep_graph(dep_graph, dependency, '\t\t' + prefix)

def iterate_dep_graph(dep_graph):
    for key, value in dep_graph.iteritems():
        print 'key: {0} len Values: {1}'.format(key, len(value))
        # print '\t{0}'.format(value)

def convert_graph_to_json(dep_graph):
    '''
    The json is list of objects where each object represents a node in the dependency graph.
    Each object has the following data:
        - Parent of the node
        - A list of Children of the node
        - The URL of the node.
        - IsRoot boolean value
        - IsLeaf boolean value.
    Skipping nodes that started from about:blank
    '''
    result_dict = dict()
    for node, children in dep_graph.iteritems():
        if node == 'about:blank':
            continue
        if node not in result_dict:
            result_dict[node] = dict()
            node_info = result_dict[node]
            node_info['isRoot'] = True
            node_info['parent'] = None
            node_info['url'] = node
        node_info = result_dict[node]
        node_info['children'] = [ child for child in children if child != node ]
        node_info['isLeaf'] = True if children is None or len(children) == 0 else False
        for child in node_info['children']:
            if child not in result_dict:
                result_dict[child] = dict()
                result_dict[child]['children'] = None
                result_dict[child]['url'] = child
                result_dict[child]['isLeaf'] = True
            result_dict[child]['parent'] = node
            result_dict[child]['isRoot'] = False
    sanity_check(result_dict)
    return result_dict

def sanity_check(result_dict):
    found_root = False
    for node, node_info in result_dict.iteritems():
        if not found_root:
            found_root = node_info['isRoot']
        elif found_root and node_info['isRoot']:
            print 'Double root for ' + node
    if not found_root:
        print 'Did not see any root...'

def dump_object_to_json(result_obj, output_dir):
    output_filename = os.path.join(output_dir, 'dependency_graph.json')
    with open(output_filename, 'wb') as output_file:
        json_str = json.dumps(result_obj)
        output_file.write(json_str)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_data_file', help='The file containing the chrome network capture file.')
    parser.add_argument('page_start_end_time', help='The file containing the page start and end time.')
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    network_activities = convert_to_object(args.network_data_file)
    page_start_end_time = common_module.parse_page_start_end_time(args.page_start_end_time)
    dep_graph = find_dependencies(network_activities, page_start_end_time)
    result_dict = convert_graph_to_json(dep_graph)
    dump_object_to_json(result_dict, args.output_dir)
    # iterate_dep_graph(dep_graph)
    # output_dep_graph(dep_graph, DEFAULT_REQUESTER, '')

