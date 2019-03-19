"""
Copyright 2019 IBM Corporation All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

Handles packaging qpylib
"""
import sys
import argparse
import setuptools


def main():
    """
    Main method for building qpylib
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Build qpylib package.")
    parser.add_argument("build", help="Type of package to build (e.g. sdist).")
    parser.add_argument("--version", required=True, help="Version of qpylib to build.")
    # Remove all arguments from argv
    args, left = parser.parse_known_args()
    sys.argv = sys.argv[:1]+left
    # Add the build type back in - this is used by setuptools
    sys.argv.append(args.build)

    # Read in the README
    with open("README.md", "r") as readme:
        long_desc = readme.read()

    # Build the package
    setuptools.setup(
        name="qpylib",
        version=args.version,
        author="IBM",
        description="qpylibc",
        long_description=long_desc,
        long_description_content_type="text/markdown",
        url="https://github.com/ibm/qpylib",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 2.7",
            "Operating System :: OS Independent",
        ],
    )

main()
