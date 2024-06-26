UID := $(shell id -u)
GID := $(shell id -g)
USER := $(shell whoami)

all:
	@mkdir ${HOME}/data >/dev/null 2>&1 || true
	@chmod 777 ${HOME}/data >/dev/null 2>&1 || true
	@mkdir ${HOME}/data/postgresql >/dev/null 2>&1 || true
	@chmod 777 ${HOME}/data/postgresql >/dev/null 2>&1 || true
	@mkdir ${HOME}/data/django >/dev/null 2>&1 || true
	@chmod 777 ${HOME}/data/django >/dev/null 2>&1 || true
	@MYHOME=${HOME} docker compose -f ./scrs/docker-compose.yml up -d --build 

down:
	@MYHOME=${HOME} docker compose -f ./scrs/docker-compose.yml down

re:
	@MYHOME=${HOME} docker compose -f ./scrs/docker-compose.yml up -d --build

clean:
	@docker exec -i django bash -c "useradd -u $(UID) -m $(USER)" >/dev/null 2>&1 || true
	@docker exec -i django bash -c "chown -R $(UID) /pong" >/dev/null 2>&1 || true
	@docker exec -i postgresql bash -c "service postgresql stop" >/dev/null 2>&1 || true
	@docker exec -i postgresql bash -c "while service postgresql status; do sleep 1; done" >/dev/null 2>&1 || true
	@docker exec -i postgresql bash -c "useradd -u $(UID) -m $(USER)" >/dev/null 2>&1 || true
	@docker exec -i postgresql bash -c "chown -R $(UID) /var/lib/postgresql" >/dev/null 2>&1 || true
	@MYHOME=${HOME} docker stop $$(docker ps -qa);\
	docker rm $$(docker ps -qa);\
	docker rmi -f $$(docker images -qa);\
	docker volume rm $$(docker volume ls -q);\
	docker network rm $$(docker network ls --filter name=scrs -q) || true;\

	@rm -rf ${HOME}/data >/dev/null 2>&1 || true
	
.PHONY: all re down clean