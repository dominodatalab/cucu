# help menu when you run just `make`
help:
	#   Provided as a convience to run commands with poetry
	#   setup  - installs the necessary development dependencies.
	#   format   - formats the code
	#   check    - checks the code
	#   test     - tests the code
	#   build    - build the dist

setup: src/*
	poetry install

format:
	poetry run ruff format .
	poetry run cucu lint --fix features

lint:
	# lint code
	poetry run ruff check .
	# lint .feature files
	poetry run cucu lint features
	# check project config
	poetry check

test:
	poetry run pytest tests
	poetry run cucu run features --workers=4

build:
	rm -f dist/*.tar.gz
	rm -f dist/*.whl
	poetry build

coverage: src/* tests/*
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
.PHONY: help format lint test build coverage
