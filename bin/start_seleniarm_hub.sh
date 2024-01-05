#!env bash
set -eo pipefail

docker kill seleniarm_hub seleniarm_node_chrome seleniarm_node_firefox || true > /dev/null 2>&1
docker rm seleniarm_hub seleniarm_node_chrome seleniarm_node_firefox || true > /dev/null 2>&1

NODE_OPTS="--link seleniarm_hub
           --env SE_NODE_OVERRIDE_MAX_SESSIONS=true
           --env SE_NODE_MAX_SESSIONS=10
           --env SE_EVENT_BUS_HOST=seleniarm_hub
           --env SE_EVENT_BUS_PUBLISH_PORT=4442
           --env SE_EVENT_BUS_SUBSCRIBE_PORT=4443"

docker run -d -p 4444:4444 --name seleniarm_hub seleniarm/hub:latest
docker run -d $NODE_OPTS --name seleniarm_node_chrome seleniarm/node-chromium:latest
docker run -d $NODE_OPTS --name seleniarm_node_firefox seleniarm/node-firefox:latest
