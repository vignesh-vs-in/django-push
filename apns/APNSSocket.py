import socket, ssl, os, logging
from django.conf import settings

logger = logging.getLogger(__name__)

class APNSSocket(object):
	def __init__(self, ssl_sock=None):
		if ssl_sock is None:
			# Use key and cert to connect to apple push server
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.ssl_sock = ssl.wrap_socket(sock,keyfile=os.path.join(settings.SITE_ROOT, "APNSClientPushKey.pem"),
				certfile=os.path.join(settings.SITE_ROOT,"APNSClientPushCert.pem"),
				server_side=False,
				do_handshake_on_connect=True)
		else:
			self.ssl_sock = ssl_sock

	def connect(self):
		self.ssl_sock.connect(('gateway.sandbox.push.apple.com', 2195))
		logger.info('Socket Connect')

	def close(self):
		self.ssl_sock.close()
		logger.info('Socket Close')

	def apnssend(self, msg):
		logger.info('Send data of len:' +  str(len(msg)))
		totalsent = 0
		while totalsent < len(msg):
			sent = self.ssl_sock.send(msg[totalsent:])
			if sent == 0:
				raise RuntimeError("socket connection broken")
			totalsent = totalsent + sent
		logger.info('Sent data of len:' + str(totalsent))

	def apnsreceive(self):
		MSGLEN = 6
		msg = ''
		while len(msg) < MSGLEN:
			chunk = self.ssl_sock.recv(MSGLEN-len(msg))
			if chunk == '':
				raise RuntimeError("socket connection broken")
			msg = msg + chunk
		return msg0