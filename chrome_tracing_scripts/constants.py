import re

METHOD = 'method'
PARAMS = 'params'
TIMESTAMP = 'timestamp'
RESPONSE = 'response'
REQUEST = 'request'
REQUEST_ID = 'requestId'
STATUS = 'status'
URL = 'url'
HEADERS = 'headers'
LINK = 'Link'
INITIATOR = 'initiator'
TYPE = 'type'
REFERER = 'Referer'
REQUEST_HEADERS = 'requestHeaders'
ENCODED_DATA_LENGTH = 'encodedDataLength'
STACK = 'stack'
CALLFRAMES = 'callFrames'
MIME_TYPE = 'mimeType'

NET_REQUEST_WILL_BE_SENT = 'Network.requestWillBeSent'
NET_RESPONSE_RECEIVED = 'Network.responseReceived'
NET_LOADING_FINISHED = 'Network.loadingFinished'
NET_LOADING_FAILED = 'Network.loadingFailed'

# Tracing constants
TRACING_NETWORK_RESOURCE_SEND_REQUEST = 'ResourceSendRequest'
TRACING_NETWORK_RESOURCE_RECEIVE_RESPONSE = 'ResourceReceiveResponse'
TRACING_NETWORK_RESOURCE_FINISH = 'ResourceFinish'
TRACING_NETWORK_PRELOAD_DISCOVERY_TIME = 'ResourcePreloadDiscovery'

TRACING_PARSING_PARSE_HTML = 'ParseHTML'
TRACING_PARSING_PARSE_AUTHOR_STYLE_SHEET = 'ParseAuthorStyleSheet'

TRACING_SCRIPT_EVALUATE_SCRIPT = 'EvaluateScript'
TRACING_SCRIPT_FUNCTION_CALL = 'FunctionCall'
TRACING_SCRIPT_TIMER_FIRE = 'TimerFire'

TRACING_EVENT_INSTANT = 'I'
TRACING_EVENT_COMPLETE = 'X'
TRACING_EVENT_BEGIN = 'B'
TRACING_EVENT_END = 'E'

TRACING_BLINK = 'blink'
TRACING_BLINK_REQUEST_RESOURCE = 'ResourceFetcher::requestResource'
TRACING_BLINK_UPDATE_STYLE = 'Document::updateStyle'
TRACING_BLINK_PRELOADED = 'LinkLoader::preloadIfNeeded'

TRACING_DISCOVERY_TIME = 'discovery_time'
TRACING_PROCESSING_TIME = 'processing_time'
TRACING_PRIORITIES = 'priorities'
TRACING_PRELOADED = 'preloaded'

def to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def to_camelcase(s):
    return re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), s)
