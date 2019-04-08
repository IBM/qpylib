#!/bin/bash

if [ $# -lt 2 ]
then
    echo "USAGE: build_image.sh <Python long version> <Python short version> [image tag]"
    echo "Example: build_image.sh 3.7.3 3.7 qpylib:build"
    exit 1
fi

source ./image.sh "${3}"
 
echo "Building docker image ${QPYLIB_DOCKER_IMAGE} with Python version ${1} (long) ${2} (short)"

docker build --build-arg QPYLIB_PYTHON_VERSION_LONG=${1} --build-arg QPYLIB_PYTHON_VERSION_SHORT=${2} \
    -t ${QPYLIB_DOCKER_IMAGE} .
