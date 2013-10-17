from apns.models import APNSToken,APNSAlert,APNSAPSPayload,APNSMessage,APNSData1,MsgQueue
import socket, ssl, pprint, struct, time, binascii, json, os, logging
from apns.APNSSocket import APNSSocket
from django.db import transaction
from django.conf import settings
from celery import Celery
from apns.constants import *

logger = logging.getLogger(__name__)

celery = Celery('tasks', broker='amqp://guest@localhost//')

@celery.task(name='Push APNS')
def pushapns():
	logger.info('Running Push APNS')
	with transaction.commit_on_success():

		msgqueue = MsgQueue.objects.all().filter(msg_sent=False).order_by('id')

		apnssock = APNSSocket() 

		startseq = 0
		endseq = 0

		# Only connect if message queue is not empty
		if msgqueue:
			apnssock.connect(APNS_SANDBOX)
			logger.info('Connected to APNS')
			startseq = msgqueue[0].id
			endseq = msgqueue[len(msgqueue)-1].id
			pushedUptoSeq = pushMsgToApns(msgqueue,apnssock)
			logger.info('Initially Pushed Upto :'+str(pushedUptoSeq) + ' of '+str(endseq))
			while endseq > pushedUptoSeq:
				# Reopen APNS Connection after encountering an error.
				apnssock.close()
				apnssock = APNSSocket()
				apnssock.connect(APNS_SANDBOX)

				msgqueue = MsgQueue.objects.all().filter(id__gt=pushedUptoSeq,id__lte=endseq).order_by('id')
				if msgqueue:
					pushedUptoSeq = pushMsgToApns(msgqueue,apnssock)
					logger.info('Iterate Pushed Upto :'+str(pushedUptoSeq) + ' of '+str(endseq))
				else:
					break

	logger.info('Close APNS Connection')
	apnssock.close()

def pushMsgToApns(msgqueue,apnssock):
	entryidsent = 0
	for entry in msgqueue:
		logger.info('Pushing Msg:' + str(entry.id))
		try:
			packet = entry.to_packet()
			if packet:
				entryidsent = entry.id
				apnssock.apnssend(packet)
				errIdentifier = checkError(apnssock)
				if errIdentifier!=0:
					return errIdentifier
				
				entry.msg_sent=True
				entry.save()
		except RuntimeError:
			logger.info('APNS Connection closed Runtime Error')
			errIdentifier = checkError(apnssock)
			if errIdentifier!=0:
				return errIdentifier

			# Re-establish ssl connection
			apnssock = APNSSocket() 
			apnssock.connect()

	"""
	Sleep few second(s) to check for any errors at the end of a transmission.
	This wait is needed as there is a delay between data sent and data recieved from APNS gateways
	"""
	time.sleep(1)
	errIdentifier = checkError(apnssock)
	if errIdentifier!=0:
		logger.info('Delayed Error')
		return errIdentifier

	return entryidsent

# TODO account for the delay between data sent and data received
def checkError(apnssock):
	err = apnssock.apnsreceive()
	if err:
		# Decode 6 Bytes of error information
		errCommand = int(binascii.hexlify(err[0]),16)
		errCode = int(binascii.hexlify(err[1]),16)
		errIdentifier = int(binascii.hexlify(err[2:]),16)
		logger.info('Error message received for ID:' + str(errIdentifier))
		if errCode == 8:
			errMsg  = MsgQueue.objects.get(id=errIdentifier)
			errMsg.error = INVALID_TOKEN
			errMsg.msg_sent=True
			errMsg.save()
			# MsgQueue.objects.all().filter(id__gt=errIdentifier).update(msg_sent=False)
			return errIdentifier
	return 0
