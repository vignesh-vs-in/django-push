from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import json, time, binascii, struct
from constants import *
from apns.BlobField import BlobField

class APNSToken(models.Model):
	token = models.CharField(max_length=64,null=False,unique=True)
	expired = models.BooleanField(default=False)
	time_expired = models.DateTimeField(blank=True,null=True)
	date_inserted = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return str(self.id)
	def was_registered_recently(self):
		return self.date_inserted >= timezone.now() - datetime.timedelta(days=1)

class APNSAlert(models.Model):
	body = models.CharField(max_length=255,null=True,blank=True)
	has_data = models.BooleanField(default=False)
	action_loc_key = models.CharField(max_length=255,null=True,blank=True)
	loc_key = models.CharField(max_length=255,null=True,blank=True)
	loc_args = models.CharField(max_length=255,null=True,blank=True)
	launch_image = models.CharField(max_length=255,null=True,blank=True)
	def to_dict(self):
		data_dict = {"body":self.body}
		return data_dict
	def __unicode__(self):
		return self.body
		
class APNSAPSPayload(models.Model):
	payload_ref = models.CharField(max_length=127)
	alert = models.ForeignKey(APNSAlert)
	badge = models.IntegerField(default=0)
	sound = models.CharField(max_length=50,null=True,blank=True)
	content_available = models.IntegerField(default=0)
	date_inserted = models.DateTimeField(auto_now_add=True)
	def to_dict(self):
		data_dict = {"aps":{"alert":self.alert.to_dict(),"badge":self.badge,"sound":self.sound}}
		return data_dict
	def __unicode__(self):
		return self.payload_ref

class APNSMessage(models.Model):
	message_ref = models.CharField(max_length=127)
	aps_payload = models.ForeignKey(APNSAPSPayload)
	has_data = models.BooleanField(default=False)
	priority = models.IntegerField(default=5)

	# ContentType Generic relations
	apns_data_type = models.ForeignKey(ContentType,null=True,blank=True)
	apns_data_id = models.PositiveIntegerField(null=True,blank=True)
	apns_data = generic.GenericForeignKey('apns_data_type','apns_data_id')

	date_inserted = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return str(self.id)+":"+self.aps_payload.payload_ref

class APNSData1(models.Model):
	value1 = models.CharField(max_length=15)
	value2 = models.CharField(max_length=15)
	APNSMessage = generic.GenericRelation(APNSMessage)
	date_inserted = models.DateTimeField(auto_now_add=True)
	def to_dict(self):
		data_dict = {"v1":self.value1,"v2":self.value2}
		return data_dict

class MsgQueue(models.Model):
	apnstoken = models.ForeignKey(APNSToken)
	apnsmessage = models.ForeignKey(APNSMessage)
	msg_sent = models.BooleanField(default=False)
	error = models.CharField(max_length=255,blank=True,null=True)
	date_inserted = models.DateTimeField(auto_now_add=True)
	# task = models.CharField(max_length=255,blank=True,null=True)

	def to_packet(self):

		def getItemFor(itemNumber,data):
			return struct.pack("!BH%ds"%(len(data)),itemNumber,len(data),data)

		def getItemWithLengthFor(itemNumber,data,dataLength):
			if dataLength == 4:
				return struct.pack("!BHI",itemNumber,dataLength,data)
			else:
				return struct.pack("!BHB",itemNumber,dataLength,data)

		expiry = time.time()
		deviceTokenHex = binascii.unhexlify(self.apnstoken.token)
		payload = json.dumps(self.apnsmessage.aps_payload.to_dict())
		priority = self.apnsmessage.priority

		# Limit the payload to 256
		if len(payload) > PAYLOAD_LIMIT:
			self.error = PAYLOAD_LIMIT_EXCEEDED
			self.msg_sent=True
			self.save()
			return None

		tokenItem = getItemFor(1,deviceTokenHex)
		payloadItem = getItemFor(2,payload)

		identifierItem = getItemWithLengthFor(3,self.id,4)
		expiryItem = getItemWithLengthFor(4,int(expiry),4)
		priorityItem = getItemWithLengthFor(5,priority,1)

		frame = tokenItem + payloadItem + identifierItem + expiryItem + priorityItem

		packetFormat = "!BI"
		packet = struct.pack(packetFormat,APNS_COMMAND,len(frame)) + frame 
		return packet

	def was_published_recently(self):
		return self.date_inserted >= timezone.now() - datetime.timedelta(days=1)
	def __unicode__(self):
		return self.apnsmessage.message_ref + ":" + str(self.apnstoken.id)

class PreTaskQueue(models.Model):
	# Django 1.6 adds support to binard field
	packet = BlobField()
	msgidentifier = models.IntegerField(default=0)
	pickedup = models.BooleanField(default=False)
	msg_sent = models.BooleanField(default=False)
	error = models.CharField(max_length=255,blank=True,null=True)