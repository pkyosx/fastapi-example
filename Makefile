IMAGE_NAME ?= fastapi-example
IMAGE_TAG ?= latest
IMAGE = $(IMAGE_NAME):$(IMAGE_TAG)
FASTAPI_EXAMPLE_PORT ?= 8888
DOCKER_COMPOSE = IMAGE=$(IMAGE) FASTAPI_EXAMPLE_PORT=$(FASTAPI_EXAMPLE_PORT) docker-compose -p fastapi-example -f docker-compose.yaml

.PHONY: build up test attach down

build: requirements.txt requirements-dev.txt
	docker build -t $(IMAGE) .

up: build
	$(DOCKER_COMPOSE) up -d --remove-orphans

test:
	$(DOCKER_COMPOSE) exec fastapi-server ./fastapi_example/bin/entrypoint-test.sh

attach:
	$(DOCKER_COMPOSE) exec fastapi-server /bin/bash

down:
	$(DOCKER_COMPOSE) down

requirements.txt: poetry.lock pyproject.toml
	poetry export --without-hashes > requirements.txt

requirements-dev.txt: poetry.lock pyproject.toml
	poetry export --without-hashes --only=dev -o requirements-dev.txt