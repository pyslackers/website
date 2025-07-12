.PHONY: clean install formatter lint types static-checks test up down setup_services start_app
help:
	@echo "make"
	@echo "    clean"
	@echo "        Remove Python/build artifacts."
	@echo "    install"
	@echo "        Create a virtual environment and install dependencies."
	@echo "    formatter"
	@echo "        Apply black formatting to code."
	@echo "    lint"
	@echo "        Lint code with pylint, and check if black formatter should be applied."
	@echo "    types"
	@echo "        Check for type errors using mypy."
	@echo "    static-checks"
	@echo "        Run all python static checks."
	@echo "    test"
	@echo "        Run pytest on tests/."
	@echo "    up"
	@echo "        Start the services and the gunicorn server"
	@echo "    down"
	@echo "        Stop the services"
	@echo "    setup_services"
	@echo "        Setup required services using tox."
	@echo "    start_app"
	@echo "        Start the gunicorn server."

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
	rm -rf .mypy_cache/
	rm -rf .venv/

install:
	uv sync --group dev

formatter:
	tox -e autoformat

format: formatter

lint:
	tox -e py312-lint

types:
	tox -e py312-mypy

static-checks: lint types

test:
	tox -e py312-test

up: setup_services start_app

setup_services:
	tox -e setup_services

start_app:
	uv run gunicorn --bind 127.0.0.1:8000 --worker-class aiohttp.GunicornWebWorker --reload pyslackersweb:app_factory

down:
	tox -e teardown_services
