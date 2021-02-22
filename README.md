# pywhlobf

## Overview

pywhlobf obfuscates your wheel distribution by compiling python source file to shared library.

## Usage

```bash
pip install pywhlobf

pywhlobf -- --help

<< OUTPUT
NAME
    pywhlobf

SYNOPSIS
    pywhlobf INPUT_WHL_OR_FOLDER OUTPUT_FOLDER <flags>

POSITIONAL ARGUMENTS
    INPUT_WHL_OR_FOLDER
        Path to the input wheel file, or the folder containing wheel file(s).
    OUTPUT_FOLDER
        Path to the output folder.

FLAGS
    --temp_folder=TEMP_FOLDER
        Type: Optional[]
        Default: None
        Path to the root of temporary folder.
    --compiler_options=COMPILER_OPTIONS
        Type: Optional[]
        Default: None
        If provided, should be a dict containing only the supported keys of `Cython.Compiler.Options`, as shown in `https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-options`. Example: --compiler_options='{"docstrings": False}'
    --cythonize_options=CYTHONIZE_OPTIONS
        Type: Optional[]
        Default: None
        If provided, should be a dict containing only the supported parameters of `Cython.Build.cythonize, as shown in `https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#Cython.Build.cythonize` and `https://github.com/cython/cython/blob/9a761a637fce6a7b70735ae2248963d63e569e14/Cython/Compiler/Options.py#L566` Example: --cythonize_options='{"compiler_directives": {"emit_code_comments": False}}'
    --processes=PROCESSES
        Type: Optional[]
        Default: None
        The number of worker processes to use. All CPUs are used by default.
    --show_warning=SHOW_WARNING
        Default: False
        If set, show the build warnings.
    --abi_tag=ABI_TAG
        Type: Optional[]
        Default: None
        If set, hardcode the ABI tag within the output wheel filename to this one.
    --platform_tag=PLATFORM_TAG
        Type: Optional[]
        Default: None
        If set, hardcode the platform tag within the output wheel filename to this one.

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
OUTPUT
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

