#!/bin/bash
# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

python -m pytest -v --cov-report xml:coverage.xml --cov-report term --cov=qpylib test
