FROM	debian:bullseye

RUN		apt-get update
RUN		apt-get upgrade
RUN 	apt install sudo nano build-essential nginx openssl -y
RUN openssl req -newkey rsa:4096 -x509 -sha256 -days 365 -nodes \
       -out /etc/nginx/cescanue.crt \
       -keyout /etc/nginx/cescanue.key \
       -subj "/C=SP/ST=Barcelona/L=Barcelona/O=42/OU=cescanue/CN=pong.42/"
COPY    ./conf/default /etc/nginx/sites-available/default
COPY    ./conf/default /etc/nginx/sites-enabled/default
CMD 	sudo service nginx start && tail -f