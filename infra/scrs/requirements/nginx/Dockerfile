FROM	debian:bullseye

RUN		apt-get update
RUN		apt-get upgrade
RUN 	apt install sudo nano build-essential nginx -y
COPY    ./conf/default /etc/nginx/sites-available/default
COPY    ./conf/default /etc/nginx/sites-enabled/default
CMD 	sudo service nginx start && tail -f