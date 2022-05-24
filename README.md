# cucu

[![CircleCI](https://circleci.com/gh/cerebrotech/cucu/tree/main.svg?style=svg&circle-token=8ad8867cae9cd93ece480ab64236c08307a4df35)](https://circleci.com/gh/cerebrotech/cucu/tree/main)

End to end testing framework that uses [cucumber](https://cucumber.io/) to
validate a product behaves as expected.

# requirements

Python 3.7+ is required and recommend setting up
[pyenv](https://github.com/pyenv/pyenv).

# installation

## from source

Clone this repo locally and then proceed to install python 3.7+ as indicated
earlier. At this point you should be able to simply run `make install` at the
top level of the source tree and it should install all required dependencies.

## from build

Within the cucu directory you can run `poetry build` and that will produce some
output like so:

```
Building cucu (0.1.0)
  - Building sdist
  - Built cucu-0.1.0.tar.gz
  - Building wheel
  - Built cucu-0.1.0-py3-none-any.whl
```

At this point you can install the file `dist/cucu-0.1.0.tar.gz` using
`pip install ....tar.gz` anywhere you'd like and have the `cucu` tool ready to
run.

# usage

## running your a test

The command `cucu run` is used to run a given test or set of tests and in its
simplest invocation you can use it like so:

```
cucu run data/features/google_kitten_search.feature
```

That would simply run the "google search for kittens test" and once it's
finished executing you can use the `cucu report` command to generate an easy
to navigate and read HTML test report which includes the steps and screenshots
from that previous test run.

*NOTE:*
By default we'll simply use the `Google Chrome` you have installed and there's
a python package that'll handle downloading chromedriver that matches your
specific local Google Chrome version.

# running exact version of chrome/firefox using docker

```
docker run -d -p 4444:4444 --env SE_NODE_MAX_SESSIONS=10 selenium/standalone-chrome:85.0
```

Which will spin up a standalone selenium chrome container and you can then use
`docker ps -a` to see where the selenium driver is listening on:

```
> docker ps -a
CONTAINER ID ... PORTS                                                NAMES
7c719f4bee29 ... 0.0.0.0:4444->4444/tcp, :::4444->4444/tcp, 5900/tcp  wizardly_haslett
```

Now when running `cucu run some.feature` you can provide
`--selenium-remote-url http://localhost:4444` and this way you'll run a very
specific version of chrome on any setup you run this on.

To ease using various custom settings you can also set most of the command line
options in a local `cucurc.yml` or in a more global place at `~/.cucurc.yml`
the same settings. For the remote url above you'd simply have the following
in your `cucurc.yml`:

```
CUCU_SELENIUM_REMOTE_URL: http://localhost:4444
```

Then you can simply run `cucu run path/to/some.feature` and `cucu` would load
the local `cucurc.yml` or `~/.cucurc.yml` settings and use those.

# running built in tests

You can run the existing `cucu` tests by simply executing `make test` and can
also check the code coverage by running `make coverage`.

# development

* Install the `pre-commit` utility. This can be done using the command
`brew install pre-commit`. (If you don't have `brew`,
[install that, first](https://brew.sh/).
* From the top-level director of the `cucu` repository,
run `pre-commit install`.

## tagging a new release

To tag a new release of cucu on your branch you can simply run `make release`
and it'll update the package version and create a new git tag which you can
then add those changes to your PR and `git push origin --tags` to push the new
tag up to git.
