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

admin.site.register(APNSToken)
admin.site.register(APNSAlert)
admin.site.register(APNSAPSPayload)
admin.site.register(APNSMessage,APNSMessageAdmin)
admin.site.register(APNSData1)
admin.site.register(MsgQueue)