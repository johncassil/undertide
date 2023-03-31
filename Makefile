.PHONY: install shell ipython test black lint count docker-build docker-push help
PROJECT=undertide
CODE=${PROJECT}/src/
ENTRYPOINTS=${PROJECT}/bin/
TESTS=${PROJECT}/tests/
DOCKER_IMG=${PROJECT}
ENVIRONMENT?=dev
VERSION=$(shell poetry version --short)

install: ## Install dependencies within a local virtual env
	poetry install
	@echo "\\n undertide has been installed!\\nIn order to use all functionality, please populate the fixme's in ${PROJECT}/.env/env"

shell: ## Spawn a shell that automatically sources the development venv
	poetry shell

ipython: ## Run ipython
	poetry run dotenv -f ${PROJECT}/.env/env run ipython

test: ## Run all tests
	poetry run dotenv -f ${PROJECT}/.env/test run pytest --cov-report term-missing --cov=src/ ${PROJECT}/tests/ -W ignore::DeprecationWarning

black: ## Auto-format all python code
	poetry run black $(CODE) $(ENTRYPOINTS) $(TESTS)

ruff: ## Auto-check all python code
	poetry run ruff $(CODE) $(ENTRYPOINTS) $(TESTS)

docker-build: ## Build the docker image
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	docker build --ssh default . --platform linux/amd64 --tag=$(DOCKER_IMG)
	rm requirements.txt

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "\\033[36m%-30s\\033[0m %s\\n", $$1, $$2}}'
