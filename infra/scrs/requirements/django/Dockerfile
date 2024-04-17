FROM	debian:bullseye

RUN		apt-get update
RUN		apt-get upgrade
RUN 	apt update && apt install  openssh-server sudo nano build-essential python3-dev python3-pip python3-venv supervisor libpq5 libpq-dev -y
RUN 	sudo echo 'root:password' | sudo chpasswd
RUN 	sudo sed "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config > tmp1; sudo cat tmp1 > /etc/ssh/sshd_config; sudo rm tmp1
RUN 	sudo pip install django
RUN 	sudo pip install psycopg2
COPY 	./conf/entry.sh /bin/entry.sh
COPY    ./conf/settings.py /tmp/settings.py
WORKDIR /pong
CMD 	sudo bash /bin/entry.sh



