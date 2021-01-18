.PHONY: docker_test local_test clean

IMG_NAME = "simon_says_test"
COMPOSE_FILE = "docker-compose-test.yml"

docker_test:
	docker-compose -f ${COMPOSE_FILE} up --build ${IMG_NAME}
	make clean_docker

local_test:
	tox -v

clean_docker:
	docker-compose -f ${COMPOSE_FILE} down