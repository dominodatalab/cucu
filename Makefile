# help menu when you run just `make`
help:
	#   install  - installs the necessary development dependencies.
	#   build    - rebuilds the existing installation and pushes any local code to the
	#              current python environment.
	#   test     - runs all of the cucu tests.
	#   lint     - lints all of the source and test code.
	#   nox      - runs all of the tests against supported python versions using nox.
	#   coverage - work in progress...

install: src/*
	pip install poetry
	poetry install

build:
	rm -f dist/*.tar.gz
	poetry build

release:
	echo "tag a new release of cucu"
	poetry version minor
	git add pyproject.toml
	git commit -m "tagged release `poetry version -s`"
	git tag `poetry version -s`

dist: build
	pip install dist/cucu-*.tar.gz


coverage: src/* tests/*
	rm -fr .coverage .coverage.*
	# this makes it so all of the underlying `cucu` command calls are run
	# with the coverage enabled even when spawned as a separate process for the
	# underlying `poetry run coverage run` process...
	COVERAGE_PROCESS_START=.coveragerc poetry run cucu run features
	poetry run coverage run -m pytest
	poetry run coverage combine .coverage.*
	poetry run coverage html --omit='*virtualenvs*'
	poetry run coverage report --omit='*virtualenvs*' --fail-under=85
	echo "open HTML coverage report at htmlcov/index.html"
