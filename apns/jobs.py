import socket, ssl, pprint, struct, time, binascii, random, json, os
from apns.models import APNSToken,APNSAlert,APNSAPSPayload,APNSMessage,APNSData1,MsgQueue
from django.conf import settings

def getItemFor(itemNumber,data):
	return struct.pack("!BH%ds"%(len(data)),itemNumber,len(data),data)

def getItemWithLengthFor(itemNumber,data,dataLength):
	if dataLength == 4:
		return struct.pack("!BHI",itemNumber,dataLength,data)
	else:
		return struct.pack("!BHB",itemNumber,dataLength,data)

def getPacket(deviceToken,payload):
	command=2
	expiry = time.time()
	deviceTokenHex = binascii.unhexlify(deviceToken)
	identifier = random.randrange(256*256)
	priority = 10

	tokenItem = getItemFor(1,deviceTokenHex)
	payloadItem = getItemFor(2,payload)

	identifierItem = getItemWithLengthFor(3,identifier,4)
	expiryItem = getItemWithLengthFor(4,int(expiry),4)
	priorityItem = getItemWithLengthFor(5,priority,1)

	frame = tokenItem + payloadItem + identifierItem + expiryItem + priorityItem

	packetFormat = "!BI"
	packet = struct.pack(packetFormat,command,len(frame)) + frame 
	return packet

def testapns():
	# Use key and cert to connect to apple push server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	ssl_sock = ssl.wrap_socket(s,keyfile=os.path.join(settings.SITE_ROOT, "APNSClientPushKey.pem"),
		certfile=os.path.join(settings.SITE_ROOT,"APNSClientPushCert.pem"),
		server_side=False,
		do_handshake_on_connect=True)

	ssl_sock.connect(('gateway.sandbox.push.apple.com', 2195))

	msgqueue = MsgQueue.objects.all().filter(msg_sent=False)

	for entry in msgqueue:
		payload = json.dumps(entry.apnsmessage.aps_payload.to_dict())
		deviceToken = entry.apnstoken.token
		totalBytes = ssl_sock.write(getPacket(deviceToken,payload))
		# print "totalBytes = %d" %(totalBytes)

	ssl_sock.close()