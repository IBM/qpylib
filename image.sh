#!/bin/bash

QPYLIB_DOCKER_IMAGE="${1}"

if [ -z "${QPYLIB_DOCKER_IMAGE}" ]
then
    QPYLIB_DOCKER_IMAGE="qpylib:build"
fi
