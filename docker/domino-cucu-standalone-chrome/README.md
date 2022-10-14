# Domino Standalone Chrome Docker Container

This directory contains the build scripts for a Domino-compatible docker container with cucu and a Selenium server
running the Chrome browser. It can be used as a Domino environment, and provided with a fully set up feature file
directory, it can run cucu tests as a Domino job. This container can be used outside of a Domino deployment.

## Building the Container

To build the container, use the following command:

```bash
docker/domino-cucu-standalone-chrome/build-docker.sh
```

## Running Tests on the Command Line

To run tests on the command line, first you will need to start the container with a test project directory mounted as a
volume.

For example:

```bash
docker run -it --rm -v $DOMINO/e2e-tests/:/e2e-tests domino-cucu-standalone-chrome:latest bash
```

The Selenium server will start, and you will see some messages indicating it has.

(Note: you can also start up the container in the background and open a shell with `docker exec` or you can automate
process shown here by running a script instead of bash).

Then you will need to install any Python dependencies:

```bash
ubuntu@e862a66b45e5:~$ cd /e2e-tests/
ubuntu@e862a66b45e5:/e2e-tests$ pip install -r requirements.txt
```

Finally, you can run your tests:

```bash
ubuntu@e862a66b45e5:/e2e-tests$ cucu run --tags=@smoke features 
```

If you wish, generate a report:

```bash
ubuntu@e862a66b45e5:/e2e-tests$ cucu report 
```

Then copy the report to your host machine:

```bash
docker cp e862a66b45e5:/e2e-tests/report /mypath/report
```

## Watching the Tests Run

To watch the tests run, you can use the built-in VNC or NoVNC server. The VNC server runs on port 5900, and the NoVNC
web server listens on port 7900. This example starts the container with both ports exposed:

```bash
docker run -it --rm -v $DOMINO/e2e-tests/:/e2e-tests -p 5900:5900 -p 7900:7900 domino-cucu-standalone-chrome:latest bash
```

In order to see the tests run, you will need to set the `CUCU_SELENIUM_REMOTE_URL` configuration variable to point to
the Selenium server running inside the container. This example shows how to do this with an environment variable:

```bash
ubuntu@e862a66b45e5:/e2e-tests$ export CUCU_SELENIUM_REMOTE_URL=http://localhost:4444
```

This can also be done in `/home/ubuntu/.cucurc.yml`

Finally, you will need to run the tests with the `--no-headless` option:

```bash
ubuntu@e862a66b45e5:/e2e-tests$ cucu run --no-headless --tags=@smoke features
```

To watch the tests run you can use one of two options. Either connect with a VNC client on port 5900 (here the address
would be `vnc://localhost:5900`) or point your browser at `http://localhost:7900/` to watch the tests run without a VNC
client. There is no VNC password.

Note: The built-in Mac "Screen Sharing" VNC Client is broken and will not work with a VNC server that has no password.
If you want to use this option, you will have to use another program like TigerVNC Viewer.

## Running the Tests in a Domino Deployment

To run the tests in a Domino deployment, you will have to use one of the images in quay.io as a custom image for an
environment. Copy the test files into your project (in this example `e2e-tests`). You will need to write script that 
automates the process of installing the python dependencies, running cucu, and generating a report (if desired). The
results f