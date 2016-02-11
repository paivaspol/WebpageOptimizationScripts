import simplejson as json

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

DEFAULT_REQUESTER = '##default'

def find_dependencies(network_activities):
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
    for network_activity in network_activities:
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

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_data_file', help='The file containing the chrome network capture file.')
    args = parser.parse_args()
    network_activities = convert_to_object(args.network_data_file)
    dep_graph = find_dependencies(network_activities)
    print '{0} {1}'.format(len(dep_graph.keys()), dep_graph.keys())
    iterate_dep_graph(dep_graph)
    # output_dep_graph(dep_graph, DEFAULT_REQUESTER, '')

