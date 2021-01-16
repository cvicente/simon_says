.PHONY: test test_local clean

IMG_NAME = "simon_says_test"

test_docker:
	docker-compose -f docker-compose-test.yml up --build ${IMG_NAME}

test_local:
	tox -v

clean_docker:
	docker stop ${IMG_NAME}
	docker rm ${IMG_NAME}
