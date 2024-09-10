# default target
all: help setup fix lint test build

help:
	#   Provided as a convience to run commands with poetry
	#   setup  - installs the necessary development dependencies.
	#   fix    - fixes code formatting
	#   lint   - lints the code
	#   test   - tests the code
	#   build  - build the dist

setup: src/*
	# make setup
	poetry install

fix:
	# make fix
	poetry run ruff format .
	poetry run cucu lint --fix features

lint:
	# make lint
	# lint code
	poetry run ruff check .
	# lint .feature files
	poetry run cucu lint features
	# check project config
	poetry check

test:
	# make test
	poetry run pytest tests
	# ℹ️ takes a while to run all cucu features
	poetry run cucu run features --workers=4 --generate-report
	# open HTML report at report/index.html

build:
	# make build
	rm -f dist/*.tar.gz
	rm -f dist/*.whl
	poetry build

coverage: src/* tests/*
	# make coverage
	rm -fr .coverage .coverage.*
	# this makes it so all of the underlying `cucu` command calls are run
	# with the coverage enabled even when spawned as a separate process for the
	# underlying `poetry run coverage run` process...
	COVERAGE_PROCESS_START=.coveragerc poetry run cucu run features --workers 6
	poetry run coverage run -m pytest
	poetry run coverage combine .coverage.*
	poetry run coverage html
	poetry run coverage xml
	poetry run coverage report
	echo "open HTML coverage report at htmlcov/index.html"

# disable caching for all make targets
.PHONY: all help format lint test build coverage
