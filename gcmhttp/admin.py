from django.contrib import admin
from gcmhttp.models import GCMessage, GCUser, GCMData1, GCMData2, MsgQueue
from django.db.models import Max
from gcmhttp import tasks

class GCMessageAdmin(admin.ModelAdmin):
	list_display = ['message_ref', 'gcm_data_type']
	ordering = ['message_ref']
	actions = ['push_to_all']

	def push_to_all(self, request, queryset):
		userlist = GCUser.objects.all()
		# Set series Id 
		msgs = MsgQueue.objects.all()
		if msgs.exists():
			seriesId = MsgQueue.objects.latest('series_id').series_id + 1
		else:
			seriesId = 1

		for msg in queryset:
			for user in userlist:
				MsgQueue(gcuser=user,gcmessage=msg,series_id=seriesId).save()

		tasks.pushgcmmsgs.map([seriesId]).delay()

		self.message_user(request, "%s message(s) to %s user(s) successfully added to MsgQueue." % (len(queryset) , len(userlist)))

	push_to_all.short_description = "Push notification to all users"

class MsgQueueAdmin(admin.ModelAdmin):
	list_display = ['id','gcuser','series_id', 'gcmessage' ,'multicast_id', 'msg_sent','message_id','registration_id','error']
	ordering = ['-id']

class GCUserAdmin(admin.ModelAdmin):
	list_display = ['id','registered_id', 'notification_key' , 'date_inserted']
	ordering = ['-id']

admin.site.register(GCMessage,GCMessageAdmin)
admin.site.register(GCUser,GCUserAdmin)
admin.site.register(GCMData1)
admin.site.register(GCMData2)
admin.site.register(MsgQueue,MsgQueueAdmin)