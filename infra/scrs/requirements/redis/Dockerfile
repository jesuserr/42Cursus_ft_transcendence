FROM	debian:bullseye

RUN 	apt update && apt install nano build-essential python3-dev python3-pip python3-venv redis-server -y
RUN		apt-get -y upgrade
RUN 	pip3 install --upgrade pip setuptools wheel
RUN 	pip3 install -U setuptools
COPY    ./conf/requirements.txt /tmp/requirements.txt
RUN 	pip3 install -r /tmp/requirements.txt
CMD		redis-server --protected-mode no
