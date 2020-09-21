#!/bin/bash
# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

# Generating documentation programatically
docs_folder="docs"
python3 -m pdoc qpylib --output-dir ./${docs_folder} --html --force --template-dir ./.pdoc_templates

# Then publish the documentation to github.io website for exemple