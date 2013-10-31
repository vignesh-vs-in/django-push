from celery import Task
from apns.APNSSocket import APNSSocket
from apns.constants import *
import logging

logger = logging.getLogger(__name__)

class APNSTask(Task):
	abstract = True
	_sock = None

	def __init__(self):
		logger.info('Initialize APNSTask')
		self.gateway = APNS_GATEWAY_SANDBOX

	@property
	def sock(self):
		if self._sock is None:
			self._sock = APNSSocket()
			self._sock.connect(self.gateway)
			logger.info('Connected to APNS')
		return self._sock

	def __del__ (self):
		logger.info('Decomposed APNSTask')
		if self._sock is not None:
			self._sock.close()