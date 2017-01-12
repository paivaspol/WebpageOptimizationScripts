import simplejson as json
import common_module
import os
import check_type

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
STACKTRACE = 'stack'
TYPE = 'type'
TIMESTAMP = 'timestamp'
WALLTIME = 'wallTime'
CALL_FRAMES = 'callFrames'
INITIAL_PRIORITY = 'initialPriority'
MIME_TYPE = 'mimeType'

DEFAULT_REQUESTER = '##default'

def find_dependencies(page, network_activities, page_start_end_time):
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
    request_id_to_order_found = dict() # Maps from the request id to the index in which the event has been found.
    request_id_to_type = dict() # Maps from the request id to the type of the resource.
    request_id_to_priority = dict() # Maps from request id to the request priority.
    url_to_request_id = dict() # Reverse mapping from the URL to the request id.
    start_time, end_time = page_start_end_time[1]
    found_page = False
    counter = 0
    requested_resources = set()
    finished_resources = set()
    for network_activity in network_activities:
        if METHOD in network_activity and \
            network_activity[METHOD] == 'Network.requestWillBeSent':
            ts = common_module.convert_to_ms(network_activity[PARAMS][WALLTIME])
            request_id = network_activity[PARAMS][REQUEST_ID]
            url = network_activity[PARAMS][REQUEST][URL]

            # if 'redirectResponse' in network_activity[PARAMS]:
            #     # if url.endswith('static.adsafeprotected.com/skeleton.js'):
            #     #     print 'request (0): ' +  url + ', ' + network_activity[PARAMS]['redirectResponse']['url']
            #     url = network_activity[PARAMS]['redirectResponse']['url']

            # print 'page: ' + page + ' document_url: ' + document_url
            if not found_page and common_module.escape_url(url) == common_module.escape_url(page):
                found_page = True

            # if not start_time <= ts <= end_time:
            #     # print 'start_time: {0} end_time: {1} ts: {2}'.format(start_time, end_time, ts)
            #     # If the event doesn't fall in the page load range.
            #     continue
            # if url.endswith('static.adsafeprotected.com/skeleton.js'):
            #     print 'request (1): ' +  url

            if not found_page:
                continue

            # if url.endswith('static.adsafeprotected.com/skeleton.js'):
            #     print 'request (2): ' +  url


            if url.startswith('data:'):
                continue

            # if url.endswith('static.adsafeprotected.com/skeleton.js'):
            #     print 'request (3): ' +  url


            requester = DEFAULT_REQUESTER
            # if url.endswith('static.adsafeprotected.com/skeleton.js'):
            #     print 'request (4): ' +  url

            if network_activity[PARAMS][INITIATOR][TYPE] == 'script' and STACKTRACE in network_activity[PARAMS][INITIATOR]:
                call_stack = network_activity[PARAMS][INITIATOR][STACKTRACE][CALL_FRAMES]
                if len(call_stack) > 0:
                    requester = call_stack[len(call_stack) - 1][URL]
            elif network_activity[PARAMS][INITIATOR][TYPE] == 'parser' and URL in network_activity[PARAMS][INITIATOR]:
                requester = network_activity[PARAMS][INITIATOR][URL]

            # if url.endswith('static.adsafeprotected.com/skeleton.js'):
            #     print 'request: {0} {1}'.format(url, requester)

            if requester is not None:
                # if url.endswith('static.adsafeprotected.com/skeleton.js'):
                #     print 'request (5): ' +  url + ' ' + requester

                if requester == '':
                    requester = DEFAULT_REQUESTER

                request_id = network_activity[PARAMS][REQUEST_ID]
                request_id_to_resource_map[request_id] = url
                request_id_to_initiator_map[request_id] = requester
                request_id_to_document_url[request_id] = network_activity[PARAMS]['documentURL']
                request_id_to_request_object[request_id] = network_activity
                request_id_to_order_found[request_id] = counter
                request_id_to_priority[request_id] = network_activity[PARAMS][REQUEST][INITIAL_PRIORITY]
                url_to_request_id[url] = request_id
                requested_resources.add(request_id)
                counter += 1

        elif METHOD in network_activity and \
            network_activity[METHOD] == 'Network.responseReceived':
            request_id = network_activity[PARAMS][REQUEST_ID]
            url = network_activity[PARAMS][RESPONSE][URL]
            # if url.endswith('tags.bluekai.com/site/2981'):
            #     print 'response: {0} {1}'.format(url, request_id_to_initiator_map[request_id])

            if request_id not in request_id_to_request_object:
                continue

            request_network_activity = request_id_to_request_object[request_id]
            response = network_activity[PARAMS][RESPONSE]
            mime_type = network_activity[PARAMS][RESPONSE][MIME_TYPE]
            request_id_to_type[request_id] = check_type.check_type(network_activity[PARAMS][TYPE], mime_type)
            if request_id in request_id_to_initiator_map and \
                request_network_activity[PARAMS][INITIATOR][TYPE] == 'parser':
                # Try to apply the second extraction rule: use the referer instead.
                if REQUEST_HEADERS in response and REFERER in response[REQUEST_HEADERS] and \
                    response[REQUEST_HEADERS][REFERER].endswith('.css'):
                    request_id_to_initiator_map[request_id] = response[REQUEST_HEADERS][REFERER]
            elif request_id in request_id_to_document_url and \
                request_id_to_initiator_map[request_id] == DEFAULT_REQUESTER:
                # Try to apply the third extraction rule: use the DocumentURL
                request_id_to_initiator_map[request_id] = request_id_to_document_url[request_id]
                # if url.endswith('tags.bluekai.com/site/2981'):
                #     print 'response (1): {0} {1} {2}'.format(url, request_id, request_id_to_initiator_map[request_id])
        elif METHOD in network_activity and \
            network_activity[METHOD] == 'Network.loadingFinished':
            request_id = network_activity[PARAMS][REQUEST_ID]
            finished_resources.add(request_id)

    unfinished_resources = requested_resources - finished_resources

    # Remove all unfinished resources
    for request_id in unfinished_resources:
        if request_id in request_id_to_initiator_map:
            del request_id_to_initiator_map[request_id]
        if request_id in request_id_to_resource_map:
            del request_id_to_resource_map[request_id]
        if request_id in request_id_to_document_url:
            del request_id_to_document_url[request_id]
        if request_id in request_id_to_request_object:
            del request_id_to_request_object[request_id]
        if request_id in request_id_to_order_found:
            del request_id_to_order_found[request_id]
        if request_id in request_id_to_type:
            del request_id_to_type[request_id]
        if request_id in request_id_to_priority:
            del request_id_to_priority[request_id]

    dep_tree = populate_dependencies(request_id_to_initiator_map, request_id_to_resource_map, url_to_request_id, page)
    return dep_tree, request_id_to_order_found, request_id_to_type, request_id_to_priority

def populate_dependencies(request_id_to_initiator_map, request_id_to_dependency_url, url_to_request_id, page_url):
    dep_tree = dict()
    for request_id, initiator in request_id_to_initiator_map.iteritems():
        # For each dependency's request id and its intiator map pair
        dependency_url = request_id_to_dependency_url[request_id]
        try:
            initiator_request_id = url_to_request_id[initiator]
        except KeyError as e:
            initiator = page_url
            initiator_request_id = url_to_request_id[page_url]

        # if 'tags.bluekai.com/site/2981' in dependency_url:
        #     print 'populate: {0} {1} {2}'.format(dependency_url, request_id, initiator_request_id)
        if (initiator, initiator_request_id) not in dep_tree:
            dep_tree[(initiator, initiator_request_id)] = []
        dep_tree[(initiator, initiator_request_id)].append((dependency_url, request_id))
    return dep_tree

def convert_to_object(network_data_file):
    '''
    Converts from string representation of JSON to an object.
    '''
    network_activities = []
    with open(network_data_file, 'rb') as input_file:
        for raw_line in input_file:
            json_str = raw_line.strip()
            try:
                json_obj = json.loads(json.loads(json_str))
            except Exception:
                json_obj = json.loads(json_str)
            network_activities.append(json_obj)
    return network_activities

def output_dep_graph(dep_graph, initiator, prefix):
    '''
    Outputs the dependency graph.
    '''
    if initiator in dep_graph:
        current_dependencies = dep_graph[initiator]
        for dependency in current_dependencies:
            print prefix + ' ' + dependency
            output_dep_graph(dep_graph, dependency, '\t' + prefix)

def iterate_dep_graph(dep_graph):
    for key, value in dep_graph.iteritems():
        print 'key: {0} len Values: {1}'.format(key, len(value))
        # print '\t{0}'.format(value)

def convert_graph_to_json(dep_graph, request_id_to_order_found, request_id_to_type, request_id_to_priority):
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
        if node[0] == 'about:blank' or node[0].startswith('data'):
            continue
        if node[0] not in result_dict:
            if node[0] == '':
                print 'yay'
            result_dict[node[0]] = dict()
            node_info = result_dict[node[0]]
            node_info['isRoot'] = True
            node_info['parent'] = None
            node_info['url'] = remove_trailing_slash(node[0])
            node_info['request_id'] = node[1]
            node_info['found_index'] = request_id_to_order_found[node[1]]
            node_info['type'] = request_id_to_type[node[1]]
            node_info['priority'] = request_id_to_priority[node[1]]

        if 'children' not in result_dict[node[0]]:
            result_dict[node[0]]['children'] = []
        result_dict[node[0]]['isLeaf'] = True if children is None or len(children) == 0 else False
        for child, request_id in children:
            if child == node[0] or child.startswith('data') or node[0] == 'about:blank':
                continue
            # print 'node[0]: {0} child: {1}, result_dict[node[0]]: {2}'.format(node[0], child, result_dict[node[0]]['children'])
            result_dict[node[0]]['children'].append(child)
            if child not in result_dict:
                result_dict[child] = dict()
                # result_dict[child]['children'] = None
                result_dict[child]['children'] = []
                result_dict[child]['url'] = child
                result_dict[child]['request_id'] = request_id
                result_dict[child]['isLeaf'] = True
                result_dict[child]['found_index'] = request_id_to_order_found[request_id]
                resource_type = request_id_to_type[request_id] if request_id in request_id_to_type else 'DEFAULT'
                result_dict[child]['type'] = resource_type
                priority = request_id_to_priority[request_id] if request_id in request_id_to_priority else 'Low' # TODO: infer from type
                result_dict[child]['priority'] = priority
            result_dict[child]['parent'] = node[0]
            result_dict[child]['isRoot'] = False
    sanity_check(result_dict)
    return result_dict

def sanity_check(result_dict):
    found_root = False
    found_root_node = None
    for node, node_info in result_dict.iteritems():
        # print node_info['isRoot']
        if found_root and node_info['isRoot']:
            print '\tDouble root for ' + node + ' ' + found_root_node
        if node_info['isRoot']:
            found_root = True
            found_root_node = node
    if not found_root:
        print '\tDid not see any root...'

def remove_trailing_slash(url):
    while url.endswith('/'):
        url = url[:len(url) - 1]
    return url

def dump_object_to_json(result_obj, output_dir):
    output_filename = os.path.join(output_dir, 'dependency_graph.json')
    with open(output_filename, 'wb') as output_file:
        json_str = json.dumps(result_obj)
        output_file.write(json_str)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page')
    parser.add_argument('network_data_file', help='The file containing the chrome network capture file.')
    parser.add_argument('page_start_end_time', help='The file containing the page start and end time.')
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--common-resource-file', default=None)
    args = parser.parse_args()
    network_activities = convert_to_object(args.network_data_file)
    page_start_end_time = common_module.parse_page_start_end_time(args.page_start_end_time)
    dep_graph, request_id_to_found_index, request_id_to_type, request_id_to_priority = find_dependencies(args.page, network_activities, page_start_end_time)
    result_dict = convert_graph_to_json(dep_graph, request_id_to_found_index, request_id_to_type, request_id_to_priority)
    dump_object_to_json(result_dict, args.output_dir)
    # iterate_dep_graph(dep_graph)
    # output_dep_graph(dep_graph, DEFAULT_REQUESTER, '')

