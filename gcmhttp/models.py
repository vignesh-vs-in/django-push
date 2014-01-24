from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from constants import *

class GCMessage(models.Model):
	message_ref = models.CharField(max_length=100) #Only used as a reference, will not be sent in the message
	collapse_key = models.CharField(max_length=255,blank=True,null=True) # Additional info here http://developer.android.com/google/gcm/adv.html#collapsible
	delay_while_idle = models.BooleanField(default=False)
	time_to_live = models.IntegerField(null=False,default= (4 * 7 * 24 * 60 * 60 )) # Four weeks
	restricted_package_name = models.CharField(max_length=150,blank=True)

	has_data = models.BooleanField(default=False)
	
	# ContentType Generic relations
	gcm_data_type = models.ForeignKey(ContentType,null=True,blank=True)
	gcm_data_id = models.PositiveIntegerField(null=True,blank=True)
	gcm_data = generic.GenericForeignKey('gcm_data_type','gcm_data_id')

	# Test request without sending message
	dry_run = models.BooleanField(default=False)

	date_inserted = models.DateTimeField(auto_now_add=True)

	def to_dict(self):
		data_dict = {}
		if self.has_data:
			payloaddata = self.gcm_data.to_dict()
			# Append 'DATA.' as per GCM guidelines. Refer http://developer.android.com/google/gcm/server.html 
			data_dict.update({DATA+self.gcm_data.data_key():payloaddata})

		if self.collapse_key:
			data_dict.update({COLLAPSE_KEY:self.collapse_key})

		if self.time_to_live!=(4 * 7 * 24 * 60 * 60):
			data_dict.update({TIME_TO_LIVE: self.time_to_live})

		if self.delay_while_idle == True:
			data_dict.update({DELAY_WHILE_IDLE: self.delay_while_idle})
			
		if self.dry_run == True:
			data_dict.update({DRY_RUN: self.dry_run})

		return data_dict

	def __unicode__(self):
		return self.message_ref

class GCUser(models.Model):
	registered_id = models.CharField(max_length=255,null=False,unique=True)
	notification_key = models.CharField(max_length=15)
	date_inserted = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return str(self.id)
	def was_registered_recently(self):
		return self.date_inserted >= timezone.now() - datetime.timedelta(days=1)

class GCMData1(models.Model):
	# String fields are recomneded by google, since the values will be converted to strings in the GCM server 
	payload_text = models.CharField(max_length=120)
	GCMessage = generic.GenericRelation(GCMessage)
	date_inserted = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.payload_text
	def data_key(self):
		return 'data1'
	def to_dict(self):
		data_dict = {"payload_text":self.payload_text}
		return data_dict

class GCMData2(models.Model):
	# String fields are recomneded by google, since the values will be converted to strings in the GCM server 
	value = models.CharField(max_length=10)
	func = models.CharField(max_length=10)
	GCMessage = generic.GenericRelation(GCMessage)
	date_inserted = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.value+" : "+self.func
	def data_key(self):
		return 'data2'
	def to_dict(self):
		data_dict = {"value":self.value,"func":self.func}
		return data_dict

class MsgQueue(models.Model):
	gcuser = models.ForeignKey(GCUser)
	gcmessage = models.ForeignKey(GCMessage)
	msg_sent = models.BooleanField(default=False)
	series_id = models.IntegerField(null=False)
	message_id = models.CharField(max_length=255,blank=True,null=True)
	registration_id = models.CharField(max_length=255,blank=True,null=True)
	error = models.CharField(max_length=255,blank=True,null=True)
	multicast_id = models.CharField(max_length=255,blank=True,null=True)
	date_inserted = models.DateTimeField(auto_now_add=True)
	def was_published_recently(self):
		return self.date_inserted >= timezone.now() - datetime.timedelta(days=1)
	def __unicode__(self):
		return self.gcuser.registered_id + ":" + self.gcmessage.message_ref 

# Add Data tables as neccessary in the below format
# class GCMData2(models.Model):
# 	yourfield1 = models.CharField(max_length=15)
# 	yourfield2 = models.CharField(max_length=15)
# 	......
# 	gcmessage = generic.GenericRelation(GCMessage)