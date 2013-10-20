Django Push
===========

Django Push is a Push notification server enabled for APNS and GCM.

Prerequisite
============

a) Install Python if you havent yet.

    sudo apt-get install python-setuptools python-dev build-essential

b) Install or upgrade Django

    pip install django

or

    pip install django --upgrade

c) Clone DjangoPush

    git clone https://github.com/vignesh-vs-in/django-push.git

Setup
=====

1) [Install Celery and RabbitMQ]. Django push uses celery for running async jobs.

APNS Setup
==========

1) Follow steps from [apple developer document to generate certificates].

2) Once you have installed the Certificate on your mac, 

a) launch Keychain Assistant on your local Mac and filter by "My Certificates" category on the left pane. You will see your certificate “Apple Development IOS Push Services”.

b) Expand this option then right click on “Apple Development IOS Push Services” > Export “Apple Development Push Services x.x.x″. Save this as APNSClientPushCert.p12 file somewhere you can access it.

c) Now right click on the "key",which is below the certificate and select "Export key". DONT password protect the keys when exporting. Save this as APNSClientPushKey.p12 file somewhere you can access it.

3)Run 

	openssl pkcs12 -clcerts -nokeys -in APNSClientPushCert.p12 -out APNSClientPushCert.pem
	openssl pkcs12 -nocerts -in APNSClientPushKey.p12 -out APNSClientPushKey.pem

4) Copy the generated .pem files to DjangoPush/DjangoPush/

GCM Setup
=========

Set your AUTHORIZATION_KEY in settings.py.

Additional Notes
================

Run Celery tasks with beat option.

	python manage.py celery worker -B

Crontabs or task intervals can be configured from admin panel.

License
=======

DjangoPush is licensed under the The [GNU General Public License]

[GNU General Public License]:http://www.gnu.org/licenses/gpl.html
[Install Celery and RabbitMQ]:http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html#broker-rabbitmq
[apple developer document to generate certificates]:https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapters/ProvisioningDevelopment.html#//apple_ref/doc/uid/TP40008194-CH104-SW1