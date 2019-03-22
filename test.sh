#!/bin/bash

# Exit on failure
set -e

DOCKER_IMAGE="${1}"
DEFAULT_IMAGE="qpylib:build"

function main() {
	# Run pylint
	if [ -z "${DOCKER_IMAGE}" ]; then
		echo "No docker image provided, building default"
		docker build -t "${DEFAULT_IMAGE}" .
		DOCKER_IMAGE="${DEFAULT_IMAGE}"
	fi
	echo "Testing qpylib"
	# Run docker image
	# Run pytest in docker container
	# With the user ID of the host container (avoids file permission issues)
	docker run -u "$(id -u):$(id -g)" -v "$(pwd)":/qpylib:Z "${DOCKER_IMAGE}" \
		/bin/bash -c "cd /qpylib && /usr/local/bin/python2.7 -m pytest -rv test"
}

main
