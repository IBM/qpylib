#!/bin/bash
# Copyright 2019 IBM Corporation All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
set -e

# Generating documentation programatically
docs_folder="docs"
python3 -m pdoc qpylib --output-dir ./${docs_folder} --html --force --template-dir ./.pdoc_templates

echo "[SUCCESS] Documentation generated under ./${docs_folder}"

# Then publish the documentation to github.io website 
docs_user="tristanlatr" # To change
docs_repo="qpylib-docs-testing" # To change

github_site="https://github.com/${docs_user}/${docs_repo}.git"

# Ask to publish
read -p "[QUESTION] Do you want to publish the documentation? [y/n]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "./${docs_repo}"
    git clone "${github_site}"
    rm -rf "./${docs_repo}/*"
    cp -R "./${docs_folder}/qpylib/" "./${docs_repo}/"
    cd "${docs_repo}"
    git add .
    git commit -m "Generate ${keyword} docs $(date)" --quiet
    git push origin master --quiet

    echo "[SUCCESS] Documentation published: https://${docs_user}.github.io/${docs_repo}"
fi