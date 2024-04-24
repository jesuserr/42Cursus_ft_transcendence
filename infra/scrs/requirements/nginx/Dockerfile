FROM	debian:bullseye

RUN		apt-get update
RUN 	apt install sudo nano build-essential nginx openssl -y
RUN		apt-get -y upgrade
RUN openssl req -newkey rsa:4096 -x509 -sha256 -days 365 -nodes \
       -out /etc/nginx/www.pong42.com.crt \
       -keyout /etc/nginx/www.pong42.com.key \
       -subj "/C=SP/ST=Barcelona/L=Barcelona/O=42/OU=cescanue/CN=www.pong42.com/"
COPY    ./conf/default /etc/nginx/sites-available/default
COPY    ./conf/default /etc/nginx/sites-enabled/default
CMD 	sudo service nginx start && tail -f