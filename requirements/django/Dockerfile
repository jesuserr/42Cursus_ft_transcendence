FROM	debian:bullseye

RUN		apt-get update
RUN 	apt update && apt install openssh-server sudo nano build-essential python3-dev python3-pip python3-venv supervisor libpq5 libpq-dev git libjpeg-dev zlib1g-dev -y
RUN		apt-get -y upgrade
RUN 	sed "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config > tmp1; sudo cat tmp1 > /etc/ssh/sshd_config; sudo rm tmp1
COPY    ./conf/armconfig.sh /tmp/armconfig.sh
RUN 	chmod 777 /tmp/armconfig.sh
RUN 	sh /tmp/armconfig.sh
ENV 	PATH="/root/.cargo/bin:${PATH}"
RUN 	pip3 install --upgrade pip setuptools wheel
COPY    ./conf/requirements.txt /tmp/requirements.txt
RUN 	pip3 install -r /tmp/requirements.txt
RUN 	pip3 install -U setuptools
RUN		mkdir -p /pong/base
COPY 	../www /pong/base/www
COPY 	./conf/entry.sh /bin/entry.sh
COPY    ./conf/settings.py /tmp/settings.py
WORKDIR /pong/base/www
CMD 	bash /bin/entry.sh
