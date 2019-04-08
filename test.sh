#!/bin/bash

source ./image.sh "${1}"

echo "Testing qpylib using docker image ${QPYLIB_DOCKER_IMAGE}"

QPYLIB_PYTEST_CMD="cd /qpylib && python -m pytest -v test"

./run_with_docker.sh ${QPYLIB_DOCKER_IMAGE} "${QPYLIB_PYTEST_CMD}"
