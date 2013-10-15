from apns.models import APNSToken,APNSAlert,APNSAPSPayload,APNSMessage,APNSData1,MsgQueue
import socket, ssl, pprint, struct, time, binascii, json, os, logging
from apns.APNSSocket import APNSSocket
from django.db import transaction
from django.conf import settings
from celery import Celery
from constants import *

logger = logging.getLogger(__name__)

celery = Celery('tasks', broker='amqp://guest@localhost//')

@celery.task(name='Push APNS')
def pushapns():

	with transaction.commit_on_success():

		msgqueue = MsgQueue.objects.all().filter(msg_sent=False).order_by('id')

		apnssock = APNSSocket() 

		# Only connect if message queue is not empty
		if msgqueue:
			apnssock.connect()
			logger.info('Connected to APNS')

		for entry in msgqueue:
			logger.info('Pushing Msg:' + str(entry.id))

			try:
				packet = entry.to_packet()
				if packet:
					totalBytes = apnssock.apnssend(packet)
			except RuntimeError:
				""" 
				APNS closes connection after receiving the errored packet.
				Since we push messages in the msgqueue oredered by id, id-1 gives the errored message.
				"""
				erroredmsg = MsgQueue.objects.all().get(pk=entry.id-1)
				erroredmsg.error = MALFORMED_PACKET

				# Re-establish ssl connection
				apnssock = APNSSocket() 
				apnssock.connect()

			entry.msg_sent=True
			entry.save()
			# print "totalBytes = %d" %(totalBytes)

	logger.info('Close APNS Connection')
	apnssock.close()