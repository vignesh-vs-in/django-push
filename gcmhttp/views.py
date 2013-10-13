from gcmhttp.models import GCMessage, GCUser, GCMData1, GCMData2, MsgQueue
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# http://localhost/gcmhttp/registeruser
@csrf_exempt
def registeruser(request):
	reg_id = request.POST['reg_id']
	gcuser = GCUser(registered_id=reg_id)
	gcuser.save()
	return HttpResponse(json.dumps({"status":"success"}))