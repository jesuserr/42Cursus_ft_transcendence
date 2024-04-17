sudo service ssh start 
echo Waiting postgress up
sleep 5
if [ -f "/pong/manage.py" ]
then
	sudo python3 manage.py runserver 0.0.0.0:8000 
else
	sudo django-admin startproject pong /pong
	sudo cp /tmp/settings.py /pong/pong/
	sudo python3 manage.py runserver 0.0.0.0:8000 
fi
