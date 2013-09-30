from django.http import HttpResponse
from gcmhttp.models import GCMessage, GCUser, GCMData1, GCMData2, MsgQueue
import json
import urllib,urllib2
from django.db import transaction
from django.conf import settings
from constants import *

# Stub
def registerID(request,regid):
	return HttpResponse("Success")

# Stub move test code elsewhere
# http://localhost:8900/gcmhttp/test
def testgcmhttp(request):

	greply = 'Nothing to See Here'
	# Fetch first 1000 ids
	msg_list = MsgQueue.objects.filter(msg_sent=False)[:1000]

	with transaction.commit_on_success():

		# Loop till msg queue is empty
		while msg_list:

			id_list = list(msg_list.values_list('gcuser__registered_id',flat=True))

			# post data to google servers wait for reply
			post_data = {REGISTRATION_IDS:id_list} 
			request = urllib2.Request(settings.GCMURL, json.dumps(post_data), HEADERS)
			greply = urllib2.urlopen(request).read()

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

def testone(request):
	post_data = {REGISTRATION_IDS:[settings.TEST_ID]} 
	request = urllib2.Request(settings.GCMURL, json.dumps(post_data), HEADERS)
	result = urllib2.urlopen(request)
	content = result.read()
	return HttpResponse(content)