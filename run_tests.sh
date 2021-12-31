#!/usr/bin/env bash

PYTHON="python3"
TESTD="$(dirname ${0})/tests"


if [[ -d "${TESTD}" ]]; then
    cd "${TESTD}"
    "${PYTHON}" -m unittest test.py
else
    echo "Tests directory ${TESTD} not found"
    exit 1
fi
