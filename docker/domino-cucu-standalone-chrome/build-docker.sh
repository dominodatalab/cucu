#!/bin/bash
set -euo pipefail
script_path="$(dirname -- "$(readlink -f "${BASH_SOURCE}")")"
project_path="$(readlink -f ${script_path}/../..)"
python_version="$(cat $project_path/.python-version)"
cd ${script_path}
docker build -t domino-cucu-standalone-chrome --build-arg PYTHON_VERSION=${python_version} .
