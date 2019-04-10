## Contributing In General

To contribute code or documentation, please submit a [pull request](https://github.com/ibm/qpylib/pulls).

### Proposing new features

If you would like to implement a new feature, please [raise an issue](https://github.com/ibm/qpylib/issues)
before sending a pull request so the feature can be discussed.

### Fixing bugs

To fix a bug, please [raise an issue](https://github.ibm.com/ibm/qpylib/issues) before sending a
pull request so it can be tracked.

### Merge approval

Any change requires approval from two maintainers before it can be merged.

For a list of the maintainers, see the [MAINTAINERS.md](MAINTAINERS.md) page.

## Legal

Each source file must include a license header for the Apache
Software License 2.0. Using the SPDX format is the simplest approach.
See existing source files for an example.

## Setup

This project has been set up so that on your local machine you can lint, test and build in mostly the same way that Travis CI does. There are three scripts you can use:

* lint.sh
* test.sh
* build.sh

The requirements.txt file in the project contains only those Python packages needed to supplement what is already provided by the Travis CI environment. If you want to run the lint/test/build scripts locally, you may need to install other packages, e.g. pytest and mock, into your local Python environment.

## Code style

Pull requests will only be accepted if they pass the linting.
Linting can be run either on your fork through Travis CI, or locally using **lint.sh**.

## Test

Pull requests will only be accepted if they pass all tests.
Tests can be run either on your fork through Travis CI, or locally using **test.sh**.

## Build

The output of **build.sh** is a tar.gz file containing the qpylib package. You can use `pip install` to install the package into your Python environment.
