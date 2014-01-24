from django.conf import settings

PAYLOAD_LIMIT_EXCEEDED = 'Payload Limit Exceeded'
PAYLOAD_LIMIT = 256

NO_ERRORS_ENCOUNTERED =  'No errors encountered'
PROCESSING_ERROR = 'Processing error'
MISSING_DEVICE_TOKEN = 'Missing device token'
MISSING_TOPIC = 'Missing topic'
MISSING_PAYLOAD = 'Missing payload'
INVALID_TOKEN_SIZE = 'Invalid token size'
INVALID_TOPIC_SIZE = 'Invalid topic size'
INVALID_PAYLOAD_SIZE = 'Invalid payload size'
INVALID_TOKEN = 'Invalid Token'
SHUTDOWN = 'Shutdown'
NONE_UNKNOWN = 'None (unknown)'

APNS_COMMAND = 2

APNS_GATEWAY_SANDBOX = 'gateway.sandbox.push.apple.com',2195
APNS_FEEDBACK_SANDBOX = 'feedback.sandbox.push.apple.com',2196

APNS_GATEWAY = 'gateway.push.apple.com',2195
APNS_FEEDBACK = 'feedback.push.apple.com',2196

FEEDBACK_LENGTH = 38

GATEWAY_WAIT_TIME = 0.2
TOTAL_GATEWAY_WAIT_TIME = 8