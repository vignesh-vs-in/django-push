from django.conf import settings

PAYLOAD_LIMIT_EXCEEDED = 'Payload Limit Exceeded'
PAYLOAD_LIMIT = 256
MALFORMED_PACKET = 'Malformed Packet'
INVALID_TOKEN = 'Invalid Token'
APNS_COMMAND = 2

APNS_GATEWAY_SANDBOX = 'gateway.sandbox.push.apple.com',2195
APNS_FEEDBACK_SANDBOX = 'feedback.sandbox.push.apple.com',2196

APNS_GATEWAY = 'gateway.push.apple.com',2195
APNS_FEEDBACK = 'feedback.push.apple.com',2196

FEEDBACK_LENGTH = 38