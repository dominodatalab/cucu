#!env bash
set -eo pipefail

docker kill selenium_hub selenium_node_chrome selenium_node_firefox selenium_node_edge || true > /dev/null 2>&1
docker rm selenium_hub selenium_node_chrome selenium_node_firefox selenium_node_edge || true > /dev/null 2>&1

NODE_OPTS="--link selenium_hub
           --env SE_NODE_OVERRIDE_MAX_SESSIONS=true
           --env SE_NODE_MAX_SESSIONS=10
           --env SE_EVENT_BUS_HOST=selenium_hub
           --env SE_EVENT_BUS_PUBLISH_PORT=4442
           --env SE_EVENT_BUS_SUBSCRIBE_PORT=4443"

docker run -d -p 4444:4444 --name selenium_hub selenium/hub:latest
docker run -d $NODE_OPTS --name selenium_node_chrome selenium/node-chrome:latest
docker run -d $NODE_OPTS --name selenium_node_firefox selenium/node-firefox:latest
docker run -d $NODE_OPTS --name selenium_node_edge selenium/node-edge:latest
