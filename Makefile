.PHONY: install shell ipython test black ruff count docker-build docker-push help
PROJECT=undertide
CODE=${PROJECT}/src/
TESTS=${PROJECT}/tests/
DOCKER_IMG=${PROJECT}
ENVIRONMENT?=dev
VERSION=$(shell poetry version --short)

install: ## Install dependencies within a local virtual env
	poetry install
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	@echo "\\n undertide has been installed!\\nIn order to use all functionality, please populate the fixme's in ${PROJECT}/.env/env"

shell: ## Spawn a shell that automatically sources the development venv
	poetry shell

ipython: ## Run ipython
	poetry run dotenv -f ${PROJECT}/.env/env run ipython

test: ## Run all tests
	rm test_report*
	poetry run dotenv -f ${PROJECT}/.env/test run pytest --cov-report term-missing --cov=undertide/src/ ${PROJECT}/tests/ -W ignore::DeprecationWarning
	rm test_report*

black: ## Auto-format all python code
	poetry run black $(CODE) $(TESTS)

ruff: ## Auto-check all python code
	poetry run ruff $(CODE) $(TESTS)

docker-build: ## Build the docker image
	docker build --ssh default . --platform linux/amd64 --tag=$(DOCKER_IMG)

bump_version: ## Bump the version
	poetry version patch
	$(shell poetry version --short > .VERSION)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "\\033[36m%-30s\\033[0m %s\\n", $$1, $$2}}'
