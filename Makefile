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
	git tag `poetry version -s`
	echo "make sure to commit your changes and then run 'git push origin --tags'"

dist: build
	pip install dist/cucu-*.tar.gz
	

test: src/* tests/*
	poetry run pytest
	export CUCU_KEEP_BROWSER_ALIVE=true
	poetry run cucu run features

lint: src/* tests/* *.py
	poetry run flake8 src tests *.py
	poetry run cucu lint data/features
	poetry run cucu lint features

nox: src/* tests/*
	poetry run nox

coverage: src/* tests/*
	poetry run coverage run --source=src/ src/cucu/cli/core.py run features
	poetry run coverage run --append --source=src/ -m pytest
	poetry run coverage html --omit='*virtualenvs*'
	poetry run coverage report --omit='*virtualenvs*' --fail-under=68
	echo "open HTML coverage report at htmlcov/index.html"

%-setup:
	terraform destroy -auto-approve terraform/docker/$(@:%-setup=selenium-%)
	terraform apply -auto-approve terraform/docker/$(@:%-setup=selenium-%)
	# overrides the cucurc.yml entries so that subsequent `cucu run ...` commands
	# are running against the existing local setup
	echo 'CUCU_SELENIUM_REMOTE_URL: http://localhost:4444' > cucurc.yml

%-destroy:
	terraform destroy -auto-approve terraform/docker/$(@:%-destroy=selenium-%)
	rm cucurc.yml
