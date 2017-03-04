import constants

class ResourceTiming:

    def get_final_timings(self):
        result = dict()
        result[constants.TRACING_NETWORK_RESOURCE_SEND_REQUEST] = self.resource_send_request[-1]
        result[constants.TRACING_NETWORK_RESOURCE_RECEIVE_RESPONSE] = self.resource_receive_response[-1]
        result[constants.TRACING_NETWORK_RESOURCE_FINISH] = self.resource_finish[-1]
        result[constants.TRACING_DISCOVERY_TIME] = self.resource_discovered[-1]
        result[constants.TRACING_PROCESSING_TIME] = ( self.start_processing[-1], self.end_processing[-1] )
        result[constants.TRACING_PRIORITIES] = self.request_priority
        return result

    def __str__(self):
        return 'url: ' + self.url + \
                '\n\trequest_id: ' + self.request_id + \
                '\n\tsend_request: ' + str(self.resource_send_request) + \
                '\n\treceive_response: ' + str(self.resource_receive_response) + \
                '\n\tresource_finish: ' + str(self.resource_finish) + \
                '\n\tresource_discovered: ' + str(self.resource_discovered) + \
                '\n\tstart_processing: ' + str(self.start_processing) + \
                '\n\tend_processing: ' + str(self.end_processing) + \
                '\n\trequest_priority: ' + str(self.request_priority) + \
                '\n\tdid_fail: ' + str(self.did_fail)

    def __init__(self, url):
        self.url = url
        self.request_id = ''
        self.request_priority = ''
        self.resource_send_request = []
        self.resource_receive_response = []
        self.resource_finish = []
        self.resource_discovered = []
        self.start_processing = []
        self.end_processing = []
        self.did_fail = False
