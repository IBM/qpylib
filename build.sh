#!/bin/bash
# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

QPYLIB_VERSION=${1:-dev}
echo "Building qpylib version ${QPYLIB_VERSION}"
echo ${QPYLIB_VERSION} > VERSION
python setup.py sdist
