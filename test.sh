#!/bin/bash
# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

# Generate an HTML coverage report only if the tests are being run locally
# and not on the CI.
GENERATE_HTML_REPORT=

if [ -z "$CI" ]
then
  GENERATE_HTML_REPORT="--cov-report html:coverage-html"
fi

python -m pytest -v --cov-report xml:coverage.xml $GENERATE_HTML_REPORT --cov-report term --cov=qpylib test


if [ -n "$CI" ]
then
  # Workaround for SonarCloud not being able to read pytest coverage reports
  sed -i 's/\/home\/runner\/work\/qpylib\/qpylib\//\/github\/workspace\//g' coverage.xml
fi
