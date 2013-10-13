from django.conf.urls import patterns, url

from apns import views

urlpatterns = patterns('',
	# url(r'^$',views.index, name='index'),
	url(r'^registertoken$', views.registertoken, name='registertoken'),
)