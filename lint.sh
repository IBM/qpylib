#!/bin/bash

python -m pylint -d C,R -r n --rcfile=.pylintrc qpylib test/*.py
