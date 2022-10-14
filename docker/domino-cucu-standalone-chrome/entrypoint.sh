#!/usr/bin/env bash
/usr/bin/supervisord --configuration /etc/supervisord.conf &

SUPERVISOR_PID=$!

function shutdown {
    echo "Trapped SIGTERM/SIGINT/x so shutting down supervisord..."
    kill -s SIGTERM ${SUPERVISOR_PID}
    wait ${SUPERVISOR_PID}
    echo "Shutdown complete"
}

trap shutdown SIGTERM SIGINT
if [ $# -gt 0 ]; then
  # retry connection every 5s x 60 which is a total of 5 minutes
  echo "Waiting for Selenium server to start...."
  curl --retry 60 --retry-delay 5 --retry-connrefused http://localhost:4444 && bash -c "$@"
fi
wait ${SUPERVISOR_PID}