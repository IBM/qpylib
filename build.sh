#!/bin/bash

# Exit on failure, don't allow uninitialised variables
set -e

VERSION="${1}"
DOCKER_IMAGE="${2}"

DEFAULT_VERSION="dev"
DEFAULT_IMAGE="qpylib:build"

function main() {
	if [ -z "${VERSION}" ]; then
		echo "No version provided, using default"
		VERSION="${DEFAULT_VERSION}"
	fi
	if [ -z "${DOCKER_IMAGE}" ]; then
		echo "No docker image provided, building default"
		docker build -t "${DEFAULT_IMAGE}" .
		DOCKER_IMAGE="${DEFAULT_IMAGE}"
	fi
	# Run docker image
	# Build python module in docker container
	# With the user ID of the host container (avoids file permission issues)
	docker run -u "$(id -u):$(id -g)" -v "$(pwd)":/qpylib:Z "${DOCKER_IMAGE}" \
		/bin/bash -c "cd /qpylib && echo ${VERSION} > /qpylib/VERSION && /usr/local/bin/python2.7 setup.py sdist"
}

main