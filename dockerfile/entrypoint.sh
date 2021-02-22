#!/bin/bash
set -e

fixuid -q

"$PYTHON_BIN"/pywhlobf "$@"
