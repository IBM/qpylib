#!/bin/bash
# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

# Generate an HTML coverage report only if the tests are being run locally
# and not on travis-ci.
GENERATE_HTML_REPORT=

if [ -z "$TRAVIS" ]
then
  GENERATE_HTML_REPORT="--cov-report html:coverage-html"
fi

python -m pytest -v --cov-report xml:coverage.xml $GENERATE_HTML_REPORT --cov-report term --cov=qpylib test
