import simplejson as json
import websocket
import threading

from time import sleep

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
TIMESTAMP = 'timestamp'

class ChromeRDPWebsocket(object):

    def __init__(self, url, target_url, device_configuration, callback):
        '''
        Initialize the object. 
        url - the websocket url
        target_url - the url to navigate to
        '''
        websocket.enableTrace(True)       

        # Conditions for a page to finish loading.
        self.originalRequestMs = None
        self.domContentEventFiredMs = None
        self.loadEventFiredMs = None
        self.tracingCollectionCompleted = False

        self.network_messages = []      # A list containing all the messages.
        self.timeline_messages = []     # A list containing all the timeline messages.
        self.url = target_url       # The URL to navigate to.
        self.callback = callback    # The callback method
        self.device_configuration = device_configuration # The device configuration
        self.debugging_url = url
        self.ws = websocket.WebSocketApp(url,\
                                        on_message = self.on_message,\
                                        on_error = self.on_error,\
                                        on_close = self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever() # start running this socket.

    def on_message(self, ws, message):
        '''
        Handle each message.
        '''
        message_obj = json.loads(message)
        # self.tracingCollectionCompleted = True
        # print 'msg: ' + message
        if METHOD in message_obj and message_obj[METHOD].startswith('Network'):
            if message_obj[METHOD] == 'Network.requestWillBeSent' and \
                message_obj[PARAMS]['initiator']['type'] == 'other':
                self.originalRequestMs = message_obj[PARAMS][TIMESTAMP] * 1000
            self.network_messages.append(message)
        elif METHOD in message_obj and message_obj[METHOD].startswith('Page'):
            if message_obj[METHOD] == 'Page.domContentEventFired':
                self.domContentEventFiredMs = message_obj[PARAMS][TIMESTAMP] * 1000
            elif message_obj[METHOD] == 'Page.loadEventFired':
                self.loadEventFiredMs = message_obj[PARAMS][TIMESTAMP] * 1000
        elif METHOD in message_obj and message_obj[METHOD] == 'Tracing.dataCollected':
            # Data collected.
            self.timeline_messages.extend(message_obj[PARAMS]['value'])
        elif METHOD in message_obj and message_obj[METHOD] == 'Tracing.tracingComplete':
            # Tracing completed
            self.tracingCollectionCompleted = True

        # if self.originalRequestMs is not None and \
        #     self.domContentEventFiredMs is not None and \
        #     self.loadEventFiredMs is not None and \
        #     not self.tracingCollectionCompleted:
        #     self.stop_trace_collection(self.ws)
       
        # if self.tracingCollectionCompleted:
        #     # A page is considerd loaded if all of these three conditions are met.
        #     print 'Start time {0}, Load completed: {1}'.format(self.originalRequestMs, self.loadEventFiredMs)
        #     self.callback(self, self.network_messages, self.timeline_messages, self.device_configuration)

        if self.originalRequestMs is not None and \
            self.domContentEventFiredMs is not None and \
            self.loadEventFiredMs is not None:
            self.disable_network_tracking(self.ws)
            self.disable_page_tracking(self.ws)
            print 'Start time {0}, Load completed: {1}'.format(self.originalRequestMs, self.loadEventFiredMs)
            self.callback(self, self.network_messages, self.timeline_messages, self.device_configuration)

    def on_error(self, ws, error):
        '''
        Handle the error.
        '''
        print error
    
    def on_close(self, ws):
        '''
        Handle when socket is closed
        '''
        print 'Socket for {0} is closed.'.format(self.url)

    def on_open(self, ws):
        '''
        Initialization logic goes here.
        '''
        self.enable_network_tracking(self.ws)
        self.enable_page_tracking(self.ws)
        # self.enable_trace_collection(self.ws)
        self.clear_cache(self.ws)
        print 'navigating to url: ' + str(self.url)
        self.navigate_to_page(self.ws, self.url)
    
    def close_connection(self):
        self.ws.close()

    def get_navigation_url(self):
        return self.url

    def clear_cache(self, debug_connection):
        '''
        Clears the cache in the browser
        '''
        clear_cache = { "id": 4, "method": "Network.clearBrowserCache" }
        debug_connection.send(json.dumps(clear_cache))
        print 'Cleared browser cache'
        sleep(0.5)

    def can_clear_cache(self, debug_connection):
        '''
        Clears the cache in the browser
        '''
        clear_cache = { "id": 4, "method": "Network.canClearBrowserCache" }
        debug_connection.send(json.dumps(clear_cache))
        print 'Cleared browser cache'
        sleep(0.5)

    def disable_network_tracking(self, debug_connection):
        '''
        Disable Network tracking in Chrome.
        '''
        disable_network = { "id": 1, "method": "Network.disable" }
        debug_connection.send(json.dumps(disable_network))
        print 'Disable network tracking.'
        sleep(0.5)

    def disable_page_tracking(self, debug_connection):
        '''
        Disable Page tracking in Chrome.
        '''
        disable_page = { 'id': 3, 'method': 'Page.disable' }
        debug_connection.send(json.dumps(disable_page))
        print 'Disable page tracking.'
        sleep(0.5)

    def enable_network_tracking(self, debug_connection):
        '''
        Enables Network tracking in Chrome.
        '''
        enable_network = { "id": 1, "method": "Network.enable" }
        debug_connection.send(json.dumps(enable_network))
        print 'Enabled network tracking.'
        sleep(0.5)
        disable_cache = { "id": 10, "method": "Network.setCacheDisabled", "params": { "cacheDisabled": True } }
        debug_connection.send(json.dumps(disable_cache))
        print 'Disable debugging connection.'
        sleep(0.5)

    def enable_page_tracking(self, debug_connection):
        '''
        Enables Page tracking in Chrome.
        '''
        enable_page = { 'id': 3, 'method': 'Page.enable' }
        debug_connection.send(json.dumps(enable_page))
        print 'Enabled page tracking.'
        sleep(0.5)

    
    def enable_runtime(self, debug_connection):
        '''
        Enables Runtime in Chrome.
        '''
        enable_page = { 'id': 3, 'method': 'Runtime.enable' }
        debug_connection.send(json.dumps(enable_page))
        print 'Enabled Runtime.'
        sleep(0.5)

    def enable_trace_collection(self, debug_connection):
        '''
        Enables the tracing collection.
        '''
        enable_trace_collection = { 'id': 4, 'method': 'Tracing.start' }
        debug_connection.send(json.dumps(enable_trace_collection))
        print 'Enabled trace collection'
        sleep(0.5)

    def stop_trace_collection(self, debug_connection):
        '''
        Enables the tracing collection.
        '''
        enable_trace_collection = { 'id': 4, 'method': 'Tracing.end' }
        debug_connection.send(json.dumps(enable_trace_collection))
        # print 'Disables trace collection'
        sleep(0.5)

    def navigate_to_page(self, debug_connection, url):
        '''
        Navigates to the url.
        '''
        navigate_to_page = json.dumps({ "id": 0, "method": "Page.navigate", "params": { "url": url }})
        debug_connection.send(navigate_to_page)
        sleep(0.5)

    def get_debugging_url(self):
        '''
        Returns the debugging url.
        '''
        return self.debugging_url
