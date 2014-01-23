from gcmhttp.models import GCMessage, GCUser, GCMData1, GCMData2, MsgQueue
from django.db import transaction
from django.conf import settings
from celery import Celery
from constants import *
import urllib,urllib2
import logging
import json


logger = logging.getLogger(__name__)

celery = Celery('tasks', broker='amqp://guest@localhost//')

@celery.task(name='Push GCM Msgs')
def pushgcmmsgs(seriesId=(0)):
	logger.info('Start Pushing Series = ' + str(seriesId))
	with transaction.commit_on_success():

		# Fetch first 1000 ids
		msg_list = MsgQueue.objects.filter(series_id=seriesId,msg_sent=False)[:1000]	

		# Loop till msg queue is empty
		while msg_list:

			id_list = list(msg_list.values_list('gcuser__registered_id',flat=True))

			# Construct the post data
			msgdtl = msg_list[0].gcmessage.to_dict()
			msgdtl.update({REGISTRATION_IDS:id_list})
			post_jsondata = json.dumps(msgdtl)
			logger.info('Post Data = ' + post_jsondata)

			# post data to google servers wait for reply
			request = urllib2.Request(settings.GCMURL, post_jsondata, HEADERS)
			greply = ''
			try:
				greply = urllib2.urlopen(request).read()
			except urllib2.HTTPError, e:
				logger.error('HTTPError = ' + str(e.code))
				break
			except urllib2.URLError, e:
				logger.error('URLError = ' + str(e.reason))
				break
			except httplib.HTTPException, e:
				logger.error('HTTPException')
				break
			except Exception:
				import traceback
				logger.error('generic exception: ' + traceback.format_exc())
				break

			# parse the JSON reply
			content = json.loads(greply)
			logger.info('Google Reply = ' + greply)

			multicast_id = content.get(MULTICAST_ID)
			results = content.get(RESULTS)

			idCounter = 0
			for msg in msg_list:
				msg.message_id = results[idCounter].get(MESSAGE_ID)
				msg.registration_id = results[idCounter].get(REGISTRATION_ID)
				msg.error = results[idCounter].get(ERROR)
				msg.multicast_id = multicast_id
				msg.msg_sent = True
				msg.save()
				idCounter = idCounter + 1

			# Fetch next set of 1000 ids
			msg_list = MsgQueue.objects.all().filter(series_id=seriesId,msg_sent=False)[:1000]

	return True		