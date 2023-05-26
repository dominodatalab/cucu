# help menu when you run just `make`
help:
	#   Warning: Use make only outside of poetry shell or virtualenvs
	#   install  - installs the necessary development dependencies.
	#   format   - formats the code
	#   check    - checks the code
	#   test     - tests the code
	#   build    - build the dist

install: src/*
	poetry install

format:
	poetry run black .
	poetry run isort src features data
	poetry run ruff . --fix
	poetry run cucu lint features

check:
	# format code
	poetry run black . --check
	# format imports
	poetry run isort --check src features data
	# lint code
	poetry run ruff .
	# lint .feature files
	poetry run cucu lint features
	# lint code for security mistakes
	poetry run bandit src features data -r -c pyproject.toml -q --severity high
	# check deps against known security issues
	poetry run safety check

test:
	poetry run pytest tests --cov=src
	poetry run cucu features --workers=4

build:
	rm -f dist/*.tar.gz
	rm -f dist/*.whl
	poetry build

qualify:
	tox

release:
	# version and commit
	poetry version minor
	git add pyproject.toml
	git commit -m "tagged release `poetry version -s`"

	# publish to test pypi
	# publish to pypi
	# publish to read the docs

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
