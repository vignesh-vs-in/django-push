from django.conf import settings

HEADERS={"Authorization":settings.AUTHORIZATION_KEY,"Content-Type" : "application/json"}

REGISTRATION_IDS = 'registration_ids'
MULTICAST_ID = 'multicast_id'
RESULTS = 'results'
MESSAGE_ID  = 'message_id'
REGISTRATION_ID = 'registration_id'
ERROR = 'error'