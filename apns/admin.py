from django.contrib import admin
from apns.models import APNSToken,APNSAlert,APNSAPSPayload,APNSMessage,APNSData1,MsgQueue

admin.site.register(APNSToken)
admin.site.register(APNSAlert)
admin.site.register(APNSAPSPayload)
admin.site.register(APNSMessage)
admin.site.register(APNSData1)
admin.site.register(MsgQueue)