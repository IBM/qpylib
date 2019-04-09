#!/bin/bash

QPYLIB_VERSION=${1:-dev}
echo "Building qpylib version ${QPYLIB_VERSION}"
echo ${QPYLIB_VERSION} > VERSION
python setup.py sdist
