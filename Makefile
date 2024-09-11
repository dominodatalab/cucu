# default target
all: help setup fix lint build test

help:
	#   Provided as a convience to run commands with uv
	#   setup  - installs the necessary development dependencies.
	#   fix    - fixes code formatting
	#   lint   - lints the code
	#   build  - build the dist
	#   test   - tests the code

setup: src/*
	# make setup
	uv sync --dev

fix:
	# make fix
	uv run ruff format .
	uv run ruff check . --fix
	uv run cucu lint --fix features

lint:
	# make lint
	# lint code
	uv run ruff check .
	# lint .feature files
	uv run cucu lint features

build:
	# make build
	rm -f dist/*.tar.gz
	rm -f dist/*.whl
	uv build

test:
	# make test
	uv run pytest tests
	# ℹ️ takes a while to run all cucu features
	uv run cucu run features --workers=4 --generate-report
	# open HTML report at report/index.html


coverage: src/* tests/*
	# make coverage
	rm -fr .coverage .coverage.*
	# this makes it so all of the underlying `cucu` command calls are run
	# with the coverage enabled even when spawned as a separate process for the
	# underlying `uv run coverage run` process...
	COVERAGE_PROCESS_START=.coveragerc uv run cucu run features --workers 6
	uv run coverage run -m pytest
	uv run coverage combine .coverage.*
	uv run coverage html
	uv run coverage xml
	uv run coverage report
	echo "open HTML coverage report at htmlcov/index.html"

# disable caching for all make targets
.PHONY: all help format lint test build coverage
