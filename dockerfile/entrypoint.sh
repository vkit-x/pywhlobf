#!/usr/bin/env bash
set -euo pipefail
trap "echo 'error: Script failed: see failed command above'" ERR

fixuid -q

if [ -z "$PYTHON_ABI_TAG" ] ; then
    echo "PYTHON_ABI_TAG not set."
    echo "Should be one of (cp35-cp35m, cp36-cp36m, cp37-cp37m, cp38-cp38, cp39-cp39, cp310-cp310))."
    echo "Abort."
    exit 1
fi

PYWHLOBF="/opt/python/${PYTHON_ABI_TAG}/bin/pywhlobf"
if [ ! -f "$PYWHLOBF" ] ; then
    echo "PYWHLOBF=${PYWHLOBF} doesn't exist, hence PYTHON_ABI_TAG=${PYTHON_ABI_TAG} is not supported."
    exit 1
fi
echo "PYWHLOBF=${PYWHLOBF}"

"$PYWHLOBF" "$@"
