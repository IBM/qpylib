## Contributing In General
Our project welcomes external contributions. If you have an itch, please feel
free to scratch it.

To contribute code or documentation, please submit a [pull request](https://github.com/ibm/qpylib/pulls).

A good way to familiarize yourself with the codebase and contribution process is
to look for and tackle low-hanging fruit in the [issue tracker](https://github.com/ibm/qpylib/issues).

### Proposing new features

If you would like to implement a new feature, please [raise an issue](https://github.com/ibm/qpylib/issues)
before sending a pull request so the feature can be discussed. This is to avoid
you wasting your valuable time working on a feature that the project developers
are not interested in accepting into the code base.

### Fixing bugs

If you would like to fix a bug, please [raise an issue](https://github.ibm.com/ibm/qpylib/issues) before sending a
pull request so it can be tracked.

### Merge approval

The project maintainers use LGTM (Looks Good To Me) in comments on the code
review to indicate acceptance. A change requires LGTMs from two of the
maintainers of each component affected.

For a list of the maintainers, see the [MAINTAINERS.md](MAINTAINERS.md) page.

## Legal

Each source file must include a license header for the Apache
Software License 2.0. Using the SPDX format is the simplest approach.
e.g.

```
Copyright <year> <holder> All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
```

## Setup
This project requires Docker to be installed so linting, testing and building can be done locally in a consistent way.
[Get docker here](https://docs.docker.com/install/)
This project has been set up so that on your local machine you can lint, test and build in mostly the same way that the CI does it. There are three commands you can use:

* lint.sh
* test.sh
* build.sh

The first time you run any of these commands it may take a while as it is building a docker image, but subsequent runs of these scripts should be fast and use the docker cache. 

## Testing
Pull requests will only be accepted if they pass all tests.
Tests can be run either on your fork through Travis CI, or locally using **test.sh**.

## Coding style guidelines
Pull requests will only be accepted if they pass the linting.
Linting can be run either on your fork through Travis CI, or locally using **lint.sh**.