# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

FROM centos:7

ARG QPYLIB_PYTHON_VERSION_LONG
ARG QPYLIB_PYTHON_VERSION_SHORT

ENV PYLINTHOME /tmp

# Add required dependencies
RUN yum install -y gcc openssl-devel bzip2-devel wget make libffi-devel

# Download and install Python
RUN cd /usr/src && \
    wget https://www.python.org/ftp/python/$QPYLIB_PYTHON_VERSION_LONG/Python-$QPYLIB_PYTHON_VERSION_LONG.tgz && \
    tar xzf Python-$QPYLIB_PYTHON_VERSION_LONG.tgz && \
    cd Python-$QPYLIB_PYTHON_VERSION_LONG && \
    ./configure --enable-optimizations && \
    make altinstall

# Install Python packages
RUN python$QPYLIB_PYTHON_VERSION_SHORT --version && \
    pip$QPYLIB_PYTHON_VERSION_SHORT install \
    flask requests cryptography pyOpenSSL pycrypto \
    pylint pytest responses wheel twine

# Ensure newly-installed Python appears first on PATH
RUN cd /usr/local/bin && \
    ln -s pip$QPYLIB_PYTHON_VERSION_SHORT pip && \
    ln -s python$QPYLIB_PYTHON_VERSION_SHORT python
