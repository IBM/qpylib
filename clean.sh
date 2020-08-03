#!/bin/bash
# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

rm -f qpylib/version.py

rm -rf dist
rm -rf qpylib.egg-info

rm -rf .pytest_cache
rm -rf qpylib/__pycache__
rm -rf qpylib/encryption/__pycache__
rm -rf test/__pycache__

rm -f .coverage
rm -f coverage.xml
rm -rf coverage-html
