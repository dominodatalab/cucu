# help menu when you run just `make`
help:
	#   install  - installs the necesary developmenet dependencies.
	#   build    - rebuilds the existing installation pushing any local code to the 
	#              current python environemnt.
	#   test     - runs all of the cucu tests.
	#   lint     - lints all of the source and test code.
	#   nox      - runs all of the tests against the support python versions using nox.
	#   coverage - work in progress...

install: src/*
	pip install poetry
	poetry install

build:
	poetry build

release:
	echo "tag a new release of cucu"
	poetry version minor
	git tag `poetry version -s`
	echo "make sure to commit your change sand then 'git push origin --tags'"

dist: build
	pip install dist/cucu-*.tar.gz
	

test: src/* tests/*
	poetry run pytest
	export CUCU_KEEP_BROWSER_ALIVE=true
	poetry run cucu run features

lint: src/* tests/* *.py
	poetry run flake8 src tests *.py

nox: src/* tests/*
	poetry run nox

coverage: src/* tests/*
	poetry run coverage run --source=src/ src/cucu/cli.py run features
	poetry run coverage run --append --source=src/ -m pytest
	poetry run coverage html --omit='*virtualenvs*'
	poetry run coverage report --omit='*virtualenvs*'
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
