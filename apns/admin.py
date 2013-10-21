from django.contrib import admin
from apns.models import APNSToken,APNSAlert,APNSAPSPayload,APNSMessage,APNSData1,MsgQueue

class APNSMessageAdmin(admin.ModelAdmin):
	list_display = ['message_ref', 'apns_data_type']
	ordering = ['message_ref']
	actions = ['push_to_all']

	def push_to_all(self, request, queryset):
		tokenlist = APNSToken.objects.all().filter(expired=False)
		for msg in queryset:
			for token in tokenlist:
				MsgQueue(apnstoken=token,apnsmessage=msg).save()
		self.message_user(request, "%s message(s) to %s token(s) successfully added to MsgQueue." % (len(queryset) , len(tokenlist)))

	push_to_all.short_description = "Push notification to all tokens"

class APNSTokenAdmin(admin.ModelAdmin):
	list_display = ['id','expired']
	ordering = ['-id']

class APNSAPSPayloadAdmin(admin.ModelAdmin):
	list_display = ['id','payload_ref','alert']
	ordering = ['-id']

class APNSAlertAdmin(admin.ModelAdmin):
	list_display = ['body','has_data']
	ordering = ['-id']

class MsgQueueAdmin(admin.ModelAdmin):
	list_display = ['id','apnstoken', 'apnsmessage' ,'msg_sent','error' ,'pickedup' ,'task']
	ordering = ['-id']
	actions = ['update_sent_false','update_sent_true']

	def update_sent_false(self, request, queryset):
		queryset.update(msg_sent=False,error=None,pickedup=False,task=None)
	update_sent_false.short_description = "Update msg_sent to False"

	def update_sent_true(self, request, queryset):
		queryset.update(msg_sent=True)
	update_sent_true.short_description = "Update msg_sent to True"

admin.site.register(APNSToken,APNSTokenAdmin)
admin.site.register(APNSAlert)
admin.site.register(APNSAPSPayload,APNSAPSPayloadAdmin)
admin.site.register(APNSMessage,APNSMessageAdmin)
admin.site.register(APNSData1)
admin.site.register(MsgQueue,MsgQueueAdmin)