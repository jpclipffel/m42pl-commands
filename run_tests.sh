#!/usr/bin/env bash
cd "$(dirname ${0})/tests"


# Runs the generic tests on all commands.
function test_generic() {
    echo "Running generic tests"
    python3 -m unittest test.py
}

# The the commands specific tests.
function test_specific() {
    echo "Running specific tests"
    python3 -m unittest test_*.py
}


case "${1}" in
    all)
        test_generic
        test_specific
        ;;
    generic)
        test_generic
        ;;
    specific)
        test_specific
        ;;
    *) cat << EOF
Usage: $(basename ${0}) <mode>

Where <mode> is one of:
* 'all': Run generic and specific test
* 'generic': Run the generic tests
* 'specific': Run the specific tests
EOF
;;
esac
