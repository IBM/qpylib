# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

# Dockerfile for local development, to allow local linting and testing
FROM centos:6
# Add dependencies required for building Python 2.7
RUN yum install -y gcc openssl-devel bzip2-devel wget
# Get Python2.7.15 and install
RUN cd /usr/src && \
	wget https://www.python.org/ftp/python/2.7.15/Python-2.7.15.tgz && \
	tar xzf Python-2.7.15.tgz && \
	cd Python-2.7.15 && \
	./configure --enable-optimizations && \
	make altinstall
# Get pip
RUN /usr/local/bin/python2.7 --version && \
	curl https://bootstrap.pypa.io/get-pip.py | /usr/local/bin/python2.7 - && \
	# Core packages
	/usr/local/bin/python2.7 -m pip install --ignore-installed flask requests cryptography pyOpenSSL pycrypto \ 
	# Linting and testing
	pylint pytest==3.0.6 responses==0.5.1 \
	  # Packaging
	setuptools wheel twine 
# Set up a user home for the non-root user in Docker
RUN mkdir /user_home
RUN chmod -R 757 /user_home