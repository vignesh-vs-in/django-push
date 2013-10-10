"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import urllib,urllib2,json
from django.test import TestCase
from gcmhttp.models import GCMessage, GCUser, GCMData1, GCMData2, MsgQueue
from gcmhttp.constants import *
from django.conf import settings

class ModelTest(TestCase):
	def setUp(self):
		gcmdata = GCMData1(payload_text='test1')
		gcmdata.save()
		msg = GCMessage(message_ref='testmsg1',collapse_key='key1',
			delay_while_idle=True,time_to_live=1100,
			restricted_package_name='com.x.x',has_data=True,
			gcm_data=gcmdata,dry_run=True)
		msg.save()

	def test_gcmessage_todict(self):
		msg = GCMessage.objects.get(message_ref='testmsg1')
		jsondict = json.loads('{"delay_while_idle": true, "collapse_key": "key1", "time_to_live": 1100, "data": {"payload_text": "test1"}, "dry_run": true}')
		msgdict = msg.to_dict()
		self.assertEqual(msgdict, jsondict)

	def test_accesstogcm(self):
		post_data = {REGISTRATION_IDS:[settings.TEST_ID],DRY_RUN:True} 
		request = urllib2.Request(settings.GCMURL, json.dumps(post_data), HEADERS)
		result = urllib2.urlopen(request)
		reply = result.read()
		content = json.loads(reply)
		success = content.get(SUCCESS)
		failure = content.get(FAILURE)
		self.assertEqual(success,1)
		self.assertEqual(failure,0)