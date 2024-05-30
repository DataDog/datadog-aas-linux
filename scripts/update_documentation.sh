#!/bin/bash

# Unless explicitly stated otherwise all files in this repository are licensed
# under the Apache License Version 2.0.
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2019-2024 Datadog, Inc.

# This script automatically opens a PR to the Documentation repo for Datadog-AAS-Wrapper

GREEN="\033[0;32m"
NC="\033[0;0m"
DOCUMENTATION_REPO_PATH=$HOME/go/src/github.com/DataDog/documentation
DOCUMENTATION_FILE=./content/en/serverless/azure_app_services/azure_app_services_linux.md

function print_color {
    printf "$GREEN$1$NC\n"
}

print_color "Creating a Github PR to update documentation"

if [ ! -d $DOCUMENTATION_REPO_PATH ]; then
    print_color "Documentation directory does not exist, cloning into $DOCUMENTATION_REPO_PATH"
    git clone  git@github.com:Datadog/documentation $DOCUMENTATION_REPO_PATH
 fi

cd $DOCUMENTATION_REPO_PATH

# Make sure they don't have any local changes
if [ ! -z "$(git status --porcelain)" ]; then
    print_color "Documentation directory is dirty -- please stash or save your changes and manually create the PR"
    exit 1
fi

print_color "Pulling latest changes from Github"
git checkout master
git pull

print_color "Checking out new branch that has version changes"
git checkout -b $USER/bump-aas-wrapper-version-$VERSION
sed -i '' -e '/.*datadog-aas-linux/{' -e 's/v[0-9]*.[0-9]*.[0-9]*/'"$VERSION"'/' -e '}' $DOCUMENTATION_FILE
git add $DOCUMENTATION_FILE

print_color "Creating commit -- please tap your Yubikey if prompted"
git commit -m "Bump AAS-WRAPPER to version $VERSION"
git push --set-upstream origin $USER/bump-aas-wrapper-version-$VERSION
dd-pr

# Reset documentation repo to clean a state that's tracking master
print_color "Resetting documentation git branch to master"
git checkout -B master origin/master