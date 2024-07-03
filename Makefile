# help menu when you run just `make`
help:
	#   Provided as a convience to run commands with poetry
	#   install  - installs the necessary development dependencies.
	#   format   - formats the code
	#   check    - checks the code
	#   test     - tests the code
	#   build    - build the dist

install: src/*
	poetry install

format:
	poetry run black .
	poetry run ruff format .
	poetry run cucu lint features

check:
	# format code
	poetry run black . --check
	# lint code
	poetry run ruff check .
	# lint .feature files
	poetry run cucu lint features
	# lint code for security mistakes
	poetry run bandit src features data -r -c pyproject.toml -q --severity high
	# check project config
	poetry check
	# prevent new secrets
	#  🔔 to update secrets ignore list use: make update-secrets
	poetry run detect-secrets-hook -n --baseline .secrets.baseline $$(git ls-files -z | xargs -0)

update-secrets:
	poetry run detect-secrets scan -n --baseline .secrets.baseline
	poetry run detect-secrets audit .secrets.baseline

test:
	poetry run pytest tests
	poetry run cucu run features --workers=4

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
	COVERAGE_PROCESS_START=.coveragerc poetry run cucu run features --workers 6
	poetry run coverage run -m pytest
	poetry run coverage combine .coverage.*
	poetry run coverage html
	poetry run coverage xml
	poetry run coverage report
	echo "open HTML coverage report at htmlcov/index.html"
