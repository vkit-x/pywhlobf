#!/usr/bin/env bash
set -euo pipefail
trap "echo 'error: Script failed: see failed command above'" ERR

declare -a PYTHON_ABIS=(
    # EOL.
    cp35-cp35m
    cp36-cp36m
    cp37-cp37m
    cp38-cp38
    cp39-cp39
)

for PYTHON_ABI in "${PYTHON_ABIS[@]}" ; do
    echo "Installing pywhlobf to ${PYTHON_ABI}."
    PIP_FILE="/opt/python/${PYTHON_ABI}/bin/pip"
    if [[ ! -f "$PIP_FILE" ]] ; then
        echo "${PYTHON_ABI} not found, skip."
        continue
    fi
    "$PIP_FILE" install --no-cache-dir -U pip
    if [ "$PYWHLOBF_CYTHON3" = 'no' ] ; then
        "$PIP_FILE" install --no-cache-dir pywhlobf=="$PYWHLOBF_VERSION"
    elif  [ "$PYWHLOBF_CYTHON3" = 'yes' ] ; then
        "$PIP_FILE" install --no-cache-dir pywhlobf[cython3]=="$PYWHLOBF_VERSION"
    else
        exit 1
done
