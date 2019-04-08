"""
Copyright 2019 IBM Corporation All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
"""
import setuptools

def main():
    with open("VERSION", "r") as version_file:
        version = version_file.read().rstrip()

    with open("README.md", "r") as readme:
        long_desc = readme.read()

    setuptools.setup(
        name = "qpylib",
        author = "IBM",
        author_email = "<>",
        version = version,
        description = "QRadar app utility library",
        long_description = long_desc,
        long_description_content_type = "text/markdown",
        license = "SPDX-License-Identifier: Apache-2.0",
        url = "https://github.com/ibm/qpylib",
        packages = setuptools.find_packages(),
        classifiers = [
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
    )

main()
