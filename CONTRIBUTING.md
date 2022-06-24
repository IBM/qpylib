# Contributing

To contribute code or documentation, please submit a [pull request](https://github.com/ibm/qpylib/pulls).

## Proposing new features

If you would like to implement a new feature, please [raise an issue](https://github.com/ibm/qpylib/issues)
before sending a pull request so that the feature can be discussed.

## Fixing bugs

To fix a bug, please [raise an issue](https://github.ibm.com/ibm/qpylib/issues) before sending a
pull request so that the bug can be tracked.

## Merge approval

Any change requires approval before it can be merged.
A list of maintainers can be found on the [MAINTAINERS](MAINTAINERS.md) page.

## Legal

Each source file must include a license header for the Apache Software License 2.0.
Using the SPDX format is the simplest approach. See existing source files for an example.

## Development

On your local machine you can lint, test and build in mostly
the same way that the CI does. There are three scripts you can use:

* `lint.sh`
* `test.sh`
* `build.sh`

The `requirements.txt` file contains the Python packages needed to run these scripts.

### Code style

Pull requests will be accepted only if `lint.sh` produces no warnings or errors.

`lint.sh` uses pylint to analyse the project's Python source code **and** unit tests.

### Test

Pull requests will be accepted only if `test.sh` reports no test failures **and**
full test coverage.

`test.sh` uses pytest and pytest-cov to execute the unit tests.

### Build

The output of `build.sh` is a `tar.gz` file and a `.whl` file.

You can take either file and use `pip install` to install qpylib as a package
into your Python 3 environment.
