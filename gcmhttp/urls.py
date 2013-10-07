from django.conf.urls import patterns, url

from gcmhttp import views

urlpatterns = patterns('',
	# url(r'^$',views.index, name='index'),
	url(r'^test$', views.testgcmhttp, name='testgcmhttp'),
	url(r'^registeruser$', views.registeruser, name='registeruser'),
)