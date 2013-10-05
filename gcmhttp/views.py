from django.http import HttpResponse
from gcmhttp.models import GCMessage, GCUser, GCMData1, GCMData2, MsgQueue
import json
import urllib,urllib2
from django.db import transaction
from django.conf import settings
from constants import *
import logging

# TODO Improve Logging
DJPLogger = logging.getLogger('view_logger')
handler1 = logging.FileHandler('usr.log')
handler1.setLevel(logging.INFO)
DJPLogger.addHandler(handler1)

# Stub
def registerID(request,regid):
	return HttpResponse("Success")

# Stub move test code elsewhere
# http://localhost:8900/gcmhttp/test
def testgcmhttp(request):

	greply = 'Nothing to See Here'

	with transaction.commit_on_success():

		uniquemsgs = MsgQueue.objects.all().filter(msg_sent=True).values_list('gcmessage',flat=True).distinct()

		for uniquemsgid in uniquemsgs:

			# Fetch first 1000 ids
			msg_list = MsgQueue.objects.filter(msg_sent=False,gcmessage_id=uniquemsgid)[:1000]	

			# Loop till msg queue is empty
			while msg_list:

				id_list = list(msg_list.values_list('gcuser__registered_id',flat=True))

				# Construct the post data
				post_data = contructPostData(msg_list[0].gcmessage,id_list)

				# post data to google servers wait for reply
				request = urllib2.Request(settings.GCMURL, json.dumps(post_data), HEADERS)
				try:
					greply = urllib2.urlopen(request).read()
				except urllib2.HTTPError, e:
					DJPLogger.error('HTTPError = ' + str(e.code))
				except urllib2.URLError, e:
					DJPLogger.error('URLError = ' + str(e.reason))
				except httplib.HTTPException, e:
					DJPLogger.error('HTTPException')
				except Exception:
					import traceback
					DJPLogger.error('generic exception: ' + traceback.format_exc())

				# parse the JSON reply
				content = json.loads(greply)
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
				msg_list = MsgQueue.objects.all().filter(msg_sent=False)[:1000]

	return HttpResponse(greply)

def contructPostData(gcmessage,id_list):
	postdata = {}
	if gcmessage:
		if gcmessage.has_data:
			payloaddata = gcmessage.gcm_data.to_dict()
			postdata.update({DATA:payloaddata})

		if gcmessage.collapse_key:
			postdata.update({COLLAPSE_KEY:gcmessage.collapse_key})

		postdata.update({DELAY_WHILE_IDLE: gcmessage.delay_while_idle})
		postdata.update({TIME_TO_LIVE: gcmessage.time_to_live})
		postdata.update({REGISTRATION_IDS:id_list})
	return postdata
		

def testone(request):
	post_data = {REGISTRATION_IDS:[settings.TEST_ID]} 
	request = urllib2.Request(settings.GCMURL, json.dumps(post_data), HEADERS)
	result = urllib2.urlopen(request)
	content = result.read()
	return HttpResponse(content)