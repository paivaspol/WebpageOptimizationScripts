import constants

class ResourceTiming:

    def get_final_timings(self):
        # print self
        result = dict()
        if len(self.resource_send_request) == 0 or \
            len(self.resource_receive_response) == 0 or \
            len(self.resource_finish) == 0:
            return None
        result[constants.URL] = self.url
        result[constants.TRACING_NETWORK_RESOURCE_SEND_REQUEST] = self.resource_send_request[0]
        result[constants.TRACING_NETWORK_RESOURCE_RECEIVE_RESPONSE] = self.resource_receive_response[0]
        result[constants.TRACING_NETWORK_RESOURCE_FINISH] = self.resource_finish[0]
        if len(self.resource_preload_time) > 0:
            result[constants.TRACING_NETWORK_PRELOAD_DISCOVERY_TIME] = self.resource_preload_time[0]
        else:
            result[constants.TRACING_NETWORK_PRELOAD_DISCOVERY_TIME] = -1

        if len(self.resource_discovered) > 0:
            result[constants.TRACING_DISCOVERY_TIME] = self.resource_discovered[0]
        else:
            result[constants.TRACING_DISCOVERY_TIME] = -1

        result[constants.TRACING_PRIORITIES] = self.request_priority
        if len(self.start_processing) > 0 and len(self.end_processing) > 0:
            result[constants.TRACING_PROCESSING_TIME] = ( self.start_processing[0], self.end_processing[0] )
        else:
            result[constants.TRACING_PROCESSING_TIME] = []

        result[constants.TRACING_PRELOADED] = self.preloaded
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
        self.resource_preload_time = []
        self.start_processing = []
        self.end_processing = []
        self.did_fail = False
        self.preloaded = False
