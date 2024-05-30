#!/bin/bash

# Unless explicitly stated otherwise all files in this repository are licensed
# under the Apache License Version 2.0.
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2019-2024 Datadog, Inc.

# This script automatically opens a PR to the Documentation repo for Datadog-AAS-Wrapper

GREEN="\033[0;32m"
NC="\033[0;0m"
DOCUMENTATION_REPO_PATH=$GITHUB_WORKSPACE/Dataog-documentation
DOCUMENTATION_FILE=$DOCUMENTATION_REPO_PATH/content/en/serverless/azure_app_services/azure_app_services_linux.md

function print_color {
    printf "$GREEN$1$NC\n"
}

cd $DOCUMENTATION_REPO_PATH

# Make sure they don't have any local changes - this shouldn't happen as the file is checked out on action execution
if [ ! -z "$(git status --porcelain)" ]; then
    print_color "Documentation directory is dirty -- please stash or save your changes and manually create the PR"
    exit 1
fi

print_color "Checking out new branch that has version changes"
git checkout -b $USER/bump-aas-wrapper-version-$VERSION
sed -i '' -e '/.*datadog-aas-linux/{' -e 's/v[0-9]*.[0-9]*.[0-9]*/'"$VERSION"'/' -e '}' $DOCUMENTATION_FILE
git add $DOCUMENTATION_FILE

print_color "Creating commit -- please tap your Yubikey if prompted"
git commit -m "Bump AAS-WRAPPER to version $VERSION"
git push --set-upstream origin $USER/bump-aas-wrapper-version-$VERSION

# Reset documentation repo to clean a state that's tracking master
print_color "Resetting documentation git branch to master"
git checkout -B master origin/master
