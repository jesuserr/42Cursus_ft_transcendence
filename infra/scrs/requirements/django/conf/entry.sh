#!/bin/bash
echo root:$ROOT_PASSWORD | sudo chpasswd
service ssh start 
if [ -f "/pong/base/www/manage.py" ]
then
	gunicorn --bind 0.0.0.0:8000 pong.wsgi --reload
else
	echo Waiting postgresql .....
	sleep 4
 	django-admin startproject pong /pong/base/www
	cp /tmp/settings.py /pong/base/www/pong/
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 manage.py createsuperuser --no-input
	python3 manage.py collectstatic --noinput
	mv /pong/base /pong/basefresh
	git clone git@github.com:jesuserr/ft_transcendence.git /pong/base
	#gunicorn --bind 0.0.0.0:8000 pong.wsgi --reload 
	#python3 manage.py runserver 0.0.0.0:8000
fi
