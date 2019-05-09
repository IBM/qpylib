#!/bin/bash
# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

rm -rf .pytest_cache
rm -f qpylib/version.py
rm -rf dist qpylib.egg-info
rm -rf qpylib/__pycache__
rm -rf "test/__pycache__"
