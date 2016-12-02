#! /bin/bash -e

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
pip install --upgrade pip
pip install .[dev]
pip install flake8==3.0.4
pip install pyflakes==1.2.3
pip install pycodestyle==2.0.0

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
SETUP_ERRORS=$(mktemp /tmp/tc-build-errors.XXXXXX)
trap "rm -f $SETUP_ERRORS" 0 2 3 15
python setup.py sdist $UPLOAD 2> >(tee $SETUP_ERRORS >&2)
if grep --quiet "Upload failed" $SETUP_ERRORS; then
  exit 1
fi
