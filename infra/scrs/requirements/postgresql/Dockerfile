FROM	debian:bullseye

RUN		apt-get update
RUN		apt-get upgrade
RUN		apt-get install -y build-essential postgresql libpq5 libpq-dev sudo 
RUN		sudo service postgresql start
RUN		sudo service postgresql restart
COPY 	./conf/create.sql /tmp/create.sql
RUN		sudo -u postgres psql -f /tmp/create.sql


