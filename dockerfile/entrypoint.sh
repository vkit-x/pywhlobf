#!/bin/bash
set -e

fixuid -q

if [ -z "$PYTHON_ABI_TAG" ] ; then
    echo "PYTHON_ABI_TAG not set (should be one of (cp36-cp36m, cp37-cp37m, cp38-cp38, cp39-cp39)), abort."
    exit 1
fi

PYWHLOBF="/opt/python/${PYTHON_ABI_TAG}/bin/pywhlobf"
if [ ! -f "$PYWHLOBF" ] ; then
    echo "PYWHLOBF=${PYWHLOBF} not exist, meaning PYTHON_ABI_TAG=${PYTHON_ABI_TAG} is not supported."
    exit 1
fi
echo "PYWHLOBF=${PYWHLOBF}"

"$PYWHLOBF" "$@"
