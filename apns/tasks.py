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
			apnssock.connect(APNS_SANDBOX)
			logger.info('Connected to APNS')

		for entry in msgqueue:
			logger.info('Pushing Msg:' + str(entry.id))

			try:
				packet = entry.to_packet()
				if packet:
					totalBytes = apnssock.apnssend(packet)
					checkError(apnssock)
			except RuntimeError:
				logger.info('APNS Connection closed Runtime Error')
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

	logger.info('Close APNS Connection')
	apnssock.close()

# TODO account for the delay between data sent and data received
def checkError(apnssock):
	err = apnssock.apnsreceive()
	if err:
		logger.info('Error msg received')
		raise RuntimeError("Error Msg Received")
