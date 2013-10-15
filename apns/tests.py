"""
These will pass when you run "manage.py test apns".

"""

from django.test import TestCase
from apns.models import APNSToken,APNSAlert,APNSAPSPayload,APNSMessage,APNSData1,MsgQueue

class SimpleTest(TestCase):
	def setUp(self):
		alert = APNSAlert(body="alerttest1",has_data=False)
		alert.save()
		apspayload = APNSAPSPayload(payload_ref="apstest1",alert=alert)
		apspayload.save()
		msg = APNSMessage(message_ref="testmsg1",aps_payload=apspayload,has_data=False)
		msg.save()

		token = APNSToken(token="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",expired=False)
		token.save()

		msgq = MsgQueue(apnstoken=token,apnsmessage=msg,msg_sent=False)
		msgq.save()

	def test_msgqueue_packet(self):
		msg = MsgQueue.objects.get(apnsmessage__message_ref="testmsg1")
		packet = msg.to_packet()
		codedpacket = '\x02\x00\x00\x00X\x01\x00 \x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef\x02\x00 {"aps": {"alert": "alerttest1"}}\x03\x00\x04\x00\x00\x00\x05\x04\x00\x04R]\x0f\x7f\x05\x00\x01\x05'

		# ignore expiry time and indentifier bytes, which changes per request
		self.assertEqual(packet[:81], codedpacket[:81])
		self.assertEqual(packet[89:], codedpacket[89:])