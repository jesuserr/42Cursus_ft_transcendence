FROM	debian:bullseye

RUN		apt-get update
RUN		apt-get upgrade
RUN		apt-get install -y build-essential postgresql libpq5 libpq-dev sudo netcat
COPY 	./conf/create.sql /tmp/create.sql
COPY 	./conf/create.sh /tmp/create.sh
RUN 	chmod 777 /tmp/create.sh
CMD		bash /tmp/create.sh



