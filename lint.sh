#!/bin/bash

source ./image.sh "${1}"

echo "Linting qpylib using docker image ${QPYLIB_DOCKER_IMAGE}"

QPYLIB_PYLINT_CMD="cd /qpylib && python -m pylint -d C,R -r n --rcfile=.pylintrc qpylib test/*.py"

./run_with_docker.sh ${QPYLIB_DOCKER_IMAGE} "${QPYLIB_PYLINT_CMD}"
