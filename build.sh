#!/bin/bash

QPYLIB_VERSION=${1:-dev}
source ./image.sh "${2}"

echo "Building qpylib version ${QPYLIB_VERSION} using docker image ${QPYLIB_DOCKER_IMAGE}"

QPYLIB_BUILD_DIST_CMD="cd /qpylib && echo ${QPYLIB_VERSION} > /qpylib/VERSION && python setup.py sdist"

./run_with_docker.sh ${QPYLIB_DOCKER_IMAGE} "${QPYLIB_BUILD_DIST_CMD}"
