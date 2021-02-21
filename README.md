# pywhlobf

## Overview

pywhlobf obfuscates your wheel distribution by compiling python source file to shared library.

## Usage

```bash
pip install pywhlobf
pywhlobf /path/to/input.whl /path/to/output/folder
```

Example:

```bash
pywhlobf wheel-0.36.2-py2.py3-none-any.whl ./tmp

<< OUTPUT
[INFO] input_whl=wheel-0.36.2-py2.py3-none-any.whl
[INFO] distribution=wheel, version=0.36.2, build_tag=None
[INFO] extract_folder=/var/folders/ts/x73fvp7d4g390cw9rx8cwkn80000gn/T/tmp7pb3euza
[INFO] Build options: compiler_options=None, cythonize_options=None, processes=None
[INFO] Building 16 python files...
[INFO] The following source files are removed:
[INFO]   wheel/metadata.py
[INFO]   wheel/macosx_libfile.py
[INFO]   wheel/util.py
[INFO]   wheel/__init__.py
[INFO]   wheel/pkginfo.py
[INFO]   wheel/bdist_wheel.py
[INFO]   wheel/wheelfile.py
[INFO]   wheel/__main__.py
[INFO]   wheel/cli/pack.py
[INFO]   wheel/cli/convert.py
[INFO]   wheel/cli/__init__.py
[INFO]   wheel/cli/unpack.py
[INFO]   wheel/vendored/__init__.py
[INFO]   wheel/vendored/packaging/tags.py
[INFO]   wheel/vendored/packaging/_typing.py
[INFO]   wheel/vendored/packaging/__init__.py
[INFO] Repacking...
[INFO] output_whl_name=wheel-0.36.2-cp38-cp38-macosx_10_15_x86_64.whl
[INFO] output_whl=tmp/wheel-0.36.2-cp38-cp38-macosx_10_15_x86_64.whl
[INFO] Done.
OUTPUT

cd ./tmp && unzip wheel-0.36.2-cp38-cp38-macosx_10_15_x86_64.whl
tree

<< OUTPUT
.
├── wheel
│   ├── __init__.cpython-38-darwin.so
│   ├── __main__.cpython-38-darwin.so
│   ├── bdist_wheel.cpython-38-darwin.so
│   ├── cli
│   │   ├── __init__.cpython-38-darwin.so
│   │   ├── convert.cpython-38-darwin.so
│   │   ├── pack.cpython-38-darwin.so
│   │   └── unpack.cpython-38-darwin.so
│   ├── macosx_libfile.cpython-38-darwin.so
│   ├── metadata.cpython-38-darwin.so
│   ├── pkginfo.cpython-38-darwin.so
│   ├── util.cpython-38-darwin.so
│   ├── vendored
│   │   ├── __init__.cpython-38-darwin.so
│   │   └── packaging
│   │       ├── __init__.cpython-38-darwin.so
│   │       ├── _typing.cpython-38-darwin.so
│   │       └── tags.cpython-38-darwin.so
│   └── wheelfile.cpython-38-darwin.so
├── wheel-0.36.2-cp38-cp38-macosx_10_15_x86_64.whl
└── wheel-0.36.2.dist-info
    ├── LICENSE.txt
    ├── METADATA
    ├── RECORD
    ├── WHEEL
    ├── entry_points.txt
    └── top_level.txt

5 directories, 23 files
OUTPUT
```

