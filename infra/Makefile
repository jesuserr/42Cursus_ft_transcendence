all:
	@mkdir ${HOME}/data >/dev/null 2>&1 || true
	@chmod 777 ${HOME}/data >/dev/null 2>&1 || true
	@mkdir ${HOME}/data/postgresql >/dev/null 2>&1 || true
	@chmod 777 ${HOME}/data/postgresql >/dev/null 2>&1 || true
	@docker-compose -f ./scrs/docker-compose.yml up -d --build 

down:
	@docker-compose -f ./scrs/docker-compose.yml down

re:
	@docker-compose -f ./scrs/docker-compose.yml up -d --build

clean:
	@docker stop $$(docker ps -qa);\
	docker rm $$(docker ps -qa);\
	docker rmi -f $$(docker images -qa);\
	docker volume rm $$(docker volume ls -q);\
	docker network rm $$(docker network ls --filter name=scrs -q) || true;\

	@rm -rf ${HOME}/data >/dev/null 2>&1 || true
	
.PHONY: all re down clean