from apns.models import APNSToken,APNSAlert,APNSAPSPayload,APNSMessage,APNSData1,MsgQueue,PreTaskQueue
import socket, ssl, pprint, struct, time, binascii, json, os, logging
from apns.APNSSocket import APNSSocket
from apns.APNSTask import APNSTask
from django.db import transaction
from django.conf import settings
from celery import Celery, task, current_task
from apns.constants import *

logger = logging.getLogger(__name__)

# ToDo Work on reporting and failures at end
@task(name='Push APNS Packet',base=APNSTask)
def pushapnspacket(packetNidentifier=(None,0)):
	packet,identifier = packetNidentifier
	logger.info('Running Push APNS Task: %s for id %d' % (current_task.request.id,identifier))
	# logger.info('Req Dtl:'+str(current_task.request))

	if packet is not None:
		logger.info('Packet None')
		try:
			current_task.sock.apnssend(packet)
		except:
			current_task.sock.reconnect()
			addFailedMsgs(identifier-1,identifier)
			return

		errIdentifier = checkError(current_task.sock)
		logger.info('Error:'+ str(errIdentifier))
		if errIdentifier != 0:
			current_task.sock.reconnect()
			addFailedMsgs(errIdentifier,identifier)
			return


# Re add msgs to pre task queue for failed messages
def addFailedMsgs(frommsgId,toId):
	fromId = PreTaskQueue.objects.filter(msgidentifier=frommsgId).order_by('-id')[0].id
	logger.info('Re-Task: %d to %d ' % (fromId,toId))
	ptqueue = PreTaskQueue.objects.all().filter(id__gt=fromId,id__lte=toId).order_by('id')
	with transaction.commit_on_success():
		tasklist=[]
		for ptentry in ptqueue:
			pt = PreTaskQueue(packet=ptentry.packet,msgidentifier=ptentry.msgidentifier,pickedup=True)
			pt.save()
			tasklist.append((binascii.unhexlify(ptentry.packet),pt.id))
		# map tasks together. Celery executes mapped tasks sequentially with the same worker.
		pushapnspacket.map(tasklist).delay()

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
# @task(name='Query APNS Feedback')
# def queryfeedback():
# 	return
# 	logger.info('Running Feedback Task:' + str(current_task.request.id))
# 	apnssock = APNSSocket()
# 	apnssock.connect(APNS_FEEDBACK_SANDBOX)
# 	msg = apnssock.apnsreceive(FEEDBACK_LENGTH)
# 	while msg:
# 		logger.info('Feedback Msg received' + msg)
# 		msg = apnssock.apnsreceive(FEEDBACK_LENGTH)
		# if msg:
		# 	expired_time = msg[0:4]
		# 	token_length = msg[5:6]
		# 	token = [7:]