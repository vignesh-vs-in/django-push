import socket, ssl, os, logging
from django.conf import settings

logger = logging.getLogger(__name__)

class APNSSocket(object):
	def __init__(self, ssl_sock=None):
		logger.info('Initialize APNSSocket')
		if ssl_sock is None:
			self.reset()
		else:
			self.ssl_sock = ssl_sock

	def reset(self):
		# Use key and cert to connect to apple push server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ssl_sock = ssl.wrap_socket(sock,keyfile=os.path.join(settings.SITE_ROOT, "APNSClientPushKey.pem"),
			certfile=os.path.join(settings.SITE_ROOT,"APNSClientPushCert.pem"),
			server_side=False,
			do_handshake_on_connect=True)

	def connect(self,gateway,blocking=True):
		self.gateway = gateway
		self.isblocking = blocking
		url,port = gateway
		self.ssl_sock.connect((url, port))
		if blocking:
			self.ssl_sock.setblocking(0)
		# logger.info('Socket Connect')

	def reconnect(self):
		self.close()
		self.reset()
		
		url,port = self.gateway
		self.ssl_sock.connect((url, port))
		if self.isblocking:
			self.ssl_sock.setblocking(0)

	def close(self):
		self.ssl_sock.close()
		# logger.info('Socket Close')

	def apnssend(self, msg):
		logger.info('Send data of len:' +  str(len(msg)))
		totalsent = 0
		while totalsent < len(msg):
			sent = self.ssl_sock.send(msg[totalsent:])
			if sent == 0:
				logger.error('Error sending message:'+msg)
				raise RuntimeError("socket connection broken")
			totalsent = totalsent + sent
		return totalsent
		logger.info('Sent data of len:' + str(totalsent))

	def apnsreceive(self,msglen=6):
		try:
			msg = self.ssl_sock.recv(msglen)
		except socket.error:
			return None
		return msg