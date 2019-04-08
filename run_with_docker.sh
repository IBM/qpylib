#!/bin/bash

QPYLIB_DOCKER_IMAGE=${1}
QPYLIB_CMD=${2}

# Use the user ID of the host container (avoids file permission issues).
# The Z flag on the -v option fixes an issue with Linux local builds.

docker run --rm -u "$(id -u):$(id -g)" -v "$(pwd)":/qpylib:Z ${QPYLIB_DOCKER_IMAGE} /bin/bash -c "${QPYLIB_CMD}"
