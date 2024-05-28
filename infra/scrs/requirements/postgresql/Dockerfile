FROM	debian:bullseye
RUN		apt-get update
RUN		apt-get update
RUN		apt-get install -y build-essential postgresql libpq5 libpq-dev sudo netcat
RUN		apt-get -y upgrade
COPY 	./conf/create.sql /tmp/create.sql
COPY 	./conf/create.sh /tmp/create.sh
RUN 	chmod 777 /tmp/create.sh
RUN     sed "s/127.0.0.1\/32/0.0.0.0\/0/g" /etc/postgresql/13/main/pg_hba.conf > tmp1; sudo cat tmp1 > /etc/postgresql/13/main/pg_hba.conf; sudo rm tmp1
RUN     echo listen_addresses = \'*\' >> /etc/postgresql/13/main/postgresql.conf
CMD		bash /tmp/create.sh



