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

	Run Celery tasks with 
	python manage.py celery beat

License
=======

DjangoPush is licensed under the The [GNU General Public License]

[GNU General Public License]:http://www.gnu.org/licenses/gpl.html
[Install Celery and RabbitMQ]:http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html#broker-rabbitmq