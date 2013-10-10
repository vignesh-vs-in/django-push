from django.conf import settings

HEADERS={"Authorization":settings.AUTHORIZATION_KEY,"Content-Type" : "application/json"}

REGISTRATION_IDS = 'registration_ids'
MULTICAST_ID = 'multicast_id'
RESULTS = 'results'
MESSAGE_ID  = 'message_id'
REGISTRATION_ID = 'registration_id'
ERROR = 'error'
DATA = 'data'
COLLAPSE_KEY = 'collapse_key'
TIME_TO_LIVE = 'time_to_live'
DELAY_WHILE_IDLE = 'delay_while_idle'
DRY_RUN = 'dry_run'
SUCCESS = 'success'
FAILURE = 'failure'