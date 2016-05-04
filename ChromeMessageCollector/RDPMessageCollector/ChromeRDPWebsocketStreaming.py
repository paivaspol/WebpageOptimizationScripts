import simplejson as json
import websocket
import threading

from time import sleep

from utils import navigation_utils

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
TIMESTAMP = 'timestamp'

WAIT = 1.0

HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'
def escape_page(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')

class ChromeRDPWebsocketStreaming(object):

    def __init__(self, url, target_url, device_configuration, user_agent_str, collect_console, callback_on_network_event, callback_page_done):
        '''
        Initialize the object. 
        url - the websocket url
        target_url - the url to navigate to
        '''
        # websocket.enableTrace(True)       

        # Conditions for a page to finish loading.
        self.originalRequestMs = None
        self.domContentEventFiredMs = None
        self.loadEventFiredMs = None
        self.tracingCollectionCompleted = False

        self.url = target_url       # The URL to navigate to.
        self.collect_console = collect_console
        self.callback_on_network_event = callback_on_network_event
        self.callback_page_done = callback_page_done    # The callback method
        self.user_agent = user_agent_str
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
        self.callback_on_network_event(self, message_obj, message)
        # self.tracingCollectionCompleted = True
        if METHOD in message_obj and message_obj[METHOD].startswith('Network'):
            if message_obj[METHOD] == 'Network.requestWillBeSent' and \
                message_obj[PARAMS]['initiator']['type'] == 'other':
                self.originalRequestMs = message_obj[PARAMS][TIMESTAMP] * 1000
        elif METHOD in message_obj and message_obj[METHOD].startswith('Page'):
            if message_obj[METHOD] == 'Page.domContentEventFired':
                self.domContentEventFiredMs = message_obj[PARAMS][TIMESTAMP] * 1000
            elif message_obj[METHOD] == 'Page.loadEventFired':
                self.loadEventFiredMs = message_obj[PARAMS][TIMESTAMP] * 1000
            elif message_obj[METHOD] == 'Page.javascriptDialogOpening':
                if message_obj[PARAMS]['type'] == 'alert' or \
                    message_obj[PARAMS]['type'] == 'beforeunload':
                    navigation_utils.handle_js_dialog(self.ws)
                elif message_obj[PARAMS]['type'] == 'confirm' or \
                    message_obj[PARAMS]['type'] == 'prompt':
                    navigation_utils.handle_js_dialog(self.ws, accept=False)

        if self.originalRequestMs is not None and \
            self.domContentEventFiredMs is not None and \
            self.loadEventFiredMs is not None:
            self.disable_network_tracking(self.ws)
            self.disable_page_tracking(self.ws)
            if self.collect_console:
                self.disable_console_tracking(self.ws)
            print 'Start time {0}, Load completed: {1}'.format(self.originalRequestMs, self.loadEventFiredMs)
            self.callback_page_done(self)

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
        
        if self.collect_console:
            self.enable_console_tracking(self.ws)

        if self.user_agent is not None:
            navigation_utils.set_user_agent(self.ws, self.user_agent)

        self.clear_cache(self.ws)
        
        # self.enable_trace_collection(self.ws)
        print 'navigating to url: ' + str(self.url)
        navigation_utils.navigate_to_page(self.ws, self.url)

    def close_connection(self):
        self.ws.close()
        print 'Connection closed'

    def get_navigation_url(self):
        return self.url

    def clear_cache(self, debug_connection):
        navigation_utils.clear_cache(debug_connection)

    def can_clear_cache(self, debug_connection):
        '''
        Clears the cache in the browser
        '''
        clear_cache = { "id": 4, "method": "Network.canClearBrowserCache" }
        debug_connection.send(json.dumps(clear_cache))
        print 'Cleared browser cache'
        sleep(WAIT)

    def disable_network_tracking(self, debug_connection):
        '''
        Disable Network tracking in Chrome.
        '''
        disable_network = { "id": 1, "method": "Network.disable" }
        debug_connection.send(json.dumps(disable_network))
        print 'Disable network tracking.'
        sleep(WAIT)

    def disable_page_tracking(self, debug_connection):
        '''
        Disable Page tracking in Chrome.
        '''
        disable_page = { 'id': 3, 'method': 'Page.disable' }
        debug_connection.send(json.dumps(disable_page))
        print 'Disable page tracking.'
        sleep(WAIT)

    def enable_network_tracking(self, debug_connection):
        '''
        Enables Network tracking in Chrome.
        '''
        enable_network = { "id": 1, "method": "Network.enable" }
        debug_connection.send(json.dumps(enable_network))
        print 'Enabled network tracking.'
        sleep(WAIT)
        disable_cache = { "id": 10, "method": "Network.setCacheDisabled", "params": { "cacheDisabled": True } }
        debug_connection.send(json.dumps(disable_cache))
        print 'Disable debugging connection.'
        sleep(WAIT)

    def enable_console_tracking(self, debug_connection):
        '''
        Enables Console Tracking.
        '''
        enable_console = { "id": 1, "method": "Console.enable" }
        debug_connection.send(json.dumps(enable_console))
        print 'Enabled network tracking.'
        sleep(WAIT)

    def disable_console_tracking(self, debug_connection):
        '''
        Disable Console tracking in Chrome.
        '''
        disable_console = { 'id': 3, 'method': 'Console.disable' }
        debug_connection.send(json.dumps(disable_console))
        print 'Disable console tracking.'
        sleep(WAIT)
    

    def enable_page_tracking(self, debug_connection):
        '''
        Enables Page tracking in Chrome.
        '''
        enable_page = { 'id': 3, 'method': 'Page.enable' }
        debug_connection.send(json.dumps(enable_page))
        print 'Enabled page tracking.'
        sleep(WAIT)

    def enable_runtime(self, debug_connection):
        '''
        Enables Runtime in Chrome.
        '''
        enable_page = { 'id': 3, 'method': 'Runtime.enable' }
        debug_connection.send(json.dumps(enable_page))
        print 'Enabled Runtime.'
        sleep(WAIT)

    def enable_trace_collection(self, debug_connection):
        '''
        Enables the tracing collection.
        '''
        enable_trace_collection = { 'id': 4, 'method': 'Tracing.start' }
        debug_connection.send(json.dumps(enable_trace_collection))
        print 'Enabled trace collection'
        sleep(WAIT)

    def stop_trace_collection(self, debug_connection):
        '''
        Enables the tracing collection.
        '''
        enable_trace_collection = { 'id': 4, 'method': 'Tracing.end' }
        debug_connection.send(json.dumps(enable_trace_collection))
        # print 'Disables trace collection'
        sleep(WAIT)

    def get_debugging_url(self):
        '''
        Returns the debugging url.
        '''
        return self.debugging_url
