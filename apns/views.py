import json
from apns.models import APNSToken
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# http://localhost/apns/registertoken
@csrf_exempt
def registertoken(request):
	token = request.POST['token']
	apnstoken = APNSToken(token=token)
	apnstoken.save()
	return HttpResponse(json.dumps({"status":"success"}))