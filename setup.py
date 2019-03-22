"""
Copyright 2019 IBM Corporation All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

Handles packaging qpylib
"""
import setuptools

def main():
    """
    Main method for building qpylib
    """

    with open("VERSION", "r") as version_file:
        version = version_file.read()

    version = version.rstrip()

    # Read in the README
    with open("README.md", "r") as readme:
        long_desc = readme.read()

    # Build the package
    setuptools.setup(
        name="qpylib",
        author="IBM",
        author_email="<>",
        version=version,
        description="QRadar app utility library",
        long_description=long_desc,
        long_description_content_type="text/markdown",
        license='SPDX-License-Identifier: Apache-2.0',
        url="https://github.com/ibm/qpylib",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 2.7",
            "Operating System :: OS Independent",
        ],
    )

main()
