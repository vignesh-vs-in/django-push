from django.contrib import admin
from apns.models import APNSToken,APNSAlert,APNSAPSPayload,APNSMessage,APNSData1,MsgQueue,PreTaskQueue
from django.db import transaction
from apns import tasks
import binascii

class APNSMessageAdmin(admin.ModelAdmin):
	list_display = ['message_ref', 'apns_data_type']
	ordering = ['message_ref']
	actions = ['push_to_all']

	def push_to_all(self, request, queryset):
		tokenlist = APNSToken.objects.all().filter(expired=False)

		with transaction.commit_on_success():
			tasklist=[]
			for msg in queryset:
				for token in tokenlist:
					# Add to Msg queue
					entry = MsgQueue(apnstoken=token,apnsmessage=msg)
					entry.save()
					# Add to PreTaskQueue

					ptentry = PreTaskQueue(packet=binascii.hexlify(entry.to_packet()),msgidentifier=entry.id,pickedup=True)
					ptentry.save()
					tasklist.append((entry.to_packet(),ptentry.id,None))

			# Add to Task Queue by mapping tasks together. Celery executes mapped tasks sequentially with the same worker.
			if tasklist:
				# Mark the last packet in the queue
				packet,ptentry,islastpacket = tasklist[-1] 
				tasklist[-1] = packet,ptentry,True
				
			tasks.pushapnspacket.map(tasklist).delay()

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

class PreTaskQueueAdmin(admin.ModelAdmin):
	list_display = ['id','msgidentifier','pickedup']
	ordering = ['-id']

class MsgQueueAdmin(admin.ModelAdmin):
	list_display = ['id','apnstoken', 'apnsmessage' ,'msg_sent','error']
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
admin.site.register(PreTaskQueue,PreTaskQueueAdmin)