#!/bin/bash
echo root:$ROOT_PASSWORD | sudo chpasswd
service ssh start 
echo Waiting postgress up
sleep 5
if [ -f "/pong/manage.py" ]
then
	cd /pong/base
	gunicorn --bind 0.0.0.0:8000 pong.wsgi
else
 	django-admin startproject pong /pong/base/www
	cp /tmp/settings.py /pong/base/www/pong/
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 manage.py createsuperuser --no-input
	python3 manage.py collectstatic --noinput
	mv /pong/base /pong/basefresh
	git clone git@github.com:jesuserr/ft_transcendence.git /pong/base
	gunicorn --bind 0.0.0.0:8000 pong.wsgi
	#python3 manage.py runserver 0.0.0.0:8000 
fi
