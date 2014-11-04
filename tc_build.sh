#! /bin/bash
set -e

LIB_NAME=pylcp
VIRTUALENV_DIR=../.virtualenvs/$LIB_NAME

if [ "$1" == "upload" ]; then
    if [ -z "$TEAMCITY_PROJECT_NAME" ]; then
        echo "Upload is only permitted from TeamCity build agents." 1>&2
        exit 1
    fi
    UPLOAD="upload --repository opsbuild2"
elif [ $# == 0 ]; then
    UPLOAD=
else
    echo Unsupported parameters: $* 1>&2
    exit 1
fi

# Initialise the virtual environment
rm -rf $VIRTUALENV_DIR
virtualenv --no-site-packages $VIRTUALENV_DIR
source $VIRTUALENV_DIR/bin/activate
pip install -r requirements-dev.txt

# Static analysis
flake8 pylcp tests setup.py

# Run unit tests
mkdir -p test_results
nosetests 2>&1 | tee test_results/unit_tests.txt
TEST_RC=${PIPESTATUS[0]}
if [ $TEST_RC -ne 0 ]; then
    exit $TEST_RC
fi

# Build distribution
python setup.py sdist $UPLOAD

