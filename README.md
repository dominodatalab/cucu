# cucu

[![CircleCI](https://circleci.com/gh/cerebrotech/cucu/tree/main.svg?style=svg&circle-token=8ad8867cae9cd93ece480ab64236c08307a4df35)](https://circleci.com/gh/cerebrotech/cucu/tree/main)

End to end testing framework that uses [cucumber](https://cucumber.io/) to
validate a product behaves as expected.

# requirements

Python 3.7+ is required and recommend setting up
[pyenv](https://github.com/pyenv/pyenv).

# installation

## from source

clone this repo locally and then proceed to install python 3.7+ as indicated
earlier at this point you should be able to simply run `make install` at the
top level of the source tree and it should install all required dependencies.

## from build

within the cucu directory you can run `poetry build` and that will produce some
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

## writing your a test

... wip ...

## running your a test

... wip ...

# running exact version of chrome/firefox using docker

```
docker run -d -p 4444:4444 selenium/standalone-chrome:85.0
```

Which will spin up a standalone selenium chrome container and you can then use
`docker ps -a` to see where the selenium driver is listening on:

```
> docker ps -a
CONTAINER ID ... PORTS                                                NAMES
7c719f4bee29 ... 0.0.0.0:4444->4444/tcp, :::4444->4444/tcp, 5900/tcp  wizardly_haslett
```

Now when running `cucu run some.feature` you can provide
`--selenium-remote-url https://localhost:4444` and this way you'll run a very
specific version of chrome on any setup you run this on.

# running built in tests

You can run the existing `cucu` tests by simply executing `make test` and can
also check the code coverage by running `make coverage`.

# development

## tagging a new release

To tag a new release of cucu on your branch you can simply run `make release`
and it'll update the package version and create a new git tag which you can
then add those changes to your PR and `git push origin --tags` to push the new
tag up to git.
