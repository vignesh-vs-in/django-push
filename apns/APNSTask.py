from celery import Task
from apns.APNSSocket import APNSSocket
from apns.constants import *
import logging

logger = logging.getLogger(__name__)

class APNSTask(Task):
	abstract = True
	_sock = None

	def __init__(self,gateway=None):
		logger.info('Initialize APNSTask')
		if gateway is None:
			self.gateway = APNS_GATEWAY_SANDBOX
		else:
			self.gateway = gateway
		if self._sock is None:		
			self._sock = APNSSocket()
			self._sock.connect(self.gateway)
			logger.info('Connected to APNS in __init__')

	@property
	def sock(self):
		if self._sock is None:
			self._sock = APNSSocket()
			self._sock.connect(self.gateway)
			logger.info('Connected to APNS')
		return self._sock

	def reconnect(self):
		self._sock.close()
		self._sock = APNSSocket()
		self._sock.connect(self.gateway)
		logger.info('Re-Connected to APNS')