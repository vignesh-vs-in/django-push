from apns.models import APNSToken,APNSAlert,APNSAPSPayload,APNSMessage,APNSData1,MsgQueue
import socket, ssl, pprint, struct, time, binascii, json, os, logging
from apns.APNSSocket import APNSSocket
from apns.APNSTask import APNSTask
from django.db import transaction
from django.conf import settings
from celery import Celery, task, current_task
from apns.constants import *

logger = logging.getLogger(__name__)

celery = Celery('tasks', broker='amqp://guest@localhost//')

@task(name='Push APNS',base=APNSTask)
def pushapns():
	logger.info('Running Push APNS Task:'+ current_task.request.id)
	with transaction.commit_on_success():

		# Updated current task id in msgs with sent flag as False and upto MSG_PER_TASK_LIMIT
		msgidbatch = MsgQueue.objects.filter(msg_sent=False,pickedup=False).order_by('id').values('pk')[:MSG_PER_TASK_LIMIT]
		MsgQueue.objects.filter(pk__in=msgidbatch).update(pickedup=True,task=current_task.request.id)

		# Fetch msgs for current task 
		msgqueue = MsgQueue.objects.all().filter(msg_sent=False,pickedup=True,task=current_task.request.id).order_by('id')

		# Proceed if message queue is not empty
		if msgqueue:
			# startseq = msgqueue[0].id
			endseq = msgqueue[len(msgqueue)-1].id
			pushedUptoSeq = pushMsgToApns(msgqueue,current_task.sock)
			logger.info('Initially Pushed %d of %d'% (pushedUptoSeq,endseq))

			while endseq > pushedUptoSeq:
				# Reopen APNS Connection after encountering an error.
				current_task.reconnect()
				msgqueue = MsgQueue.objects.all().filter(id__gt=pushedUptoSeq,id__lte=endseq,msg_sent=False,pickedup=True,task=current_task.request.id).order_by('id')
				if msgqueue:
					pushedUptoSeq = pushMsgToApns(msgqueue,current_task.sock)
					logger.info('Iterate Pushed Upto : %d of %d' %(pushedUptoSeq,endseq))
				else:
					break

	logger.info('Completed Push APNS Task:'+ str(current_task.request.id))

def pushMsgToApns(msgqueue,apnssock):
	msgqueueIdPushed = 0

	for entry in msgqueue:
		logger.info('Pushing Msg:' + str(entry.id))
		try:
			packet = entry.to_packet()
			if packet:
				msgqueueIdPushed = entry.id
				apnssock.apnssend(packet)
				# Return the error idendifier. Apple ignores all the ids sent after the error identifier
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

	"""
	Sleep few second(s) to check for any errors at the end of a transmission.
	This wait is needed as there is a delay between the data sent and data recieved from APNS gateways
	"""

	timespent = 0
	while timespent < TOTAL_GATEWAY_WAIT_TIME:
		errIdentifier = checkError(apnssock)
		if errIdentifier!=0:
			logger.info('Delayed Error')
			return errIdentifier

		time.sleep(GATEWAY_WAIT_TIME)
		timespent = timespent + GATEWAY_WAIT_TIME

	return msgqueueIdPushed

def checkError(apnssock):
	err = apnssock.apnsreceive()
	errIdentifier = 0	
	if err:
		# Decode 6 Bytes of error information
		errCommand = int(binascii.hexlify(err[0]),16)
		errCode = int(binascii.hexlify(err[1]),16)
		errIdentifier = int(binascii.hexlify(err[2:]),16)
		logger.info('Error message received for ID: %d' %(errIdentifier))
		errMsg  = MsgQueue.objects.get(id=errIdentifier)

		if errCode == 0:
			errMsg.error = NO_ERRORS_ENCOUNTERED
		elif errCode == 1:
			errMsg.error = PROCESSING_ERROR
		elif errCode == 2:
			errMsg.error = MISSING_DEVICE_TOKEN
		elif errCode == 3:
			errMsg.error = MISSING_TOPIC
		elif errCode == 4:
			errMsg.error = MISSING_PAYLOAD
		elif errCode == 5:
			errMsg.error = INVALID_TOKEN_SIZE
		elif errCode == 6:
			errMsg.error = INVALID_TOPIC_SIZE
		elif errCode == 7:
			errMsg.error = INVALID_PAYLOAD_SIZE
		elif errCode == 8:
			errMsg.error = INVALID_TOKEN
		elif errCode == 10:
			errMsg.error = SHUTDOWN
		elif errCode > 10:
			errMsg.error = NONE_UNKNOWN

		errMsg.msg_sent=True
		errMsg.save()

	return errIdentifier

# Schedule queryfeedback dailiy to get the list of device tokens that is expired.
@task(name='Query APNS Feedback')
def queryfeedback():
	return
	logger.info('Running Feedback Task:' + str(current_task.request.id))
	apnssock = APNSSocket()
	apnssock.connect(APNS_FEEDBACK_SANDBOX)
	msg = apnssock.apnsreceive(FEEDBACK_LENGTH)
	while msg:
		logger.info('Feedback Msg received' + msg)
		msg = apnssock.apnsreceive(FEEDBACK_LENGTH)
		# if msg:
		# 	expired_time = msg[0:4]
		# 	token_length = msg[5:6]
		# 	token = [7:]
