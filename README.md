English | [简体中文](README_zh.md)

# pywhlobf

## Overview

pywhlobf obfuscates your wheel distribution by compiling python source file to shared library.

## Usage

### `manylinux` based docker images

Following images are based on [pypa/manylinux](https://github.com/pypa/manylinux) platforms, with the tagging format as `<pywhlobf_version>-<platform_tag>`. The full list can be found in [pywhlobf/tags](https://hub.docker.com/r/pywhlobf/pywhlobf/tags). If you want to obfuscate a wheel to support a different target platform, i.e. macOS or Windows platform, you should install `pywhlobf` from PyPI in the target platform and execute manually, as described in the next section.

* `pywhlobf/pywhlobf:0.2.6-manylinux_2_24_x86_64`
* `pywhlobf/pywhlobf:0.2.6-manylinux_2_24_i686`
* `pywhlobf/pywhlobf:0.2.6-manylinux1_x86_64`
* `pywhlobf/pywhlobf:0.2.6-manylinux1_i686`
* `pywhlobf/pywhlobf:0.2.6-manylinux2010_x86_64`
* `pywhlobf/pywhlobf:0.2.6-manylinux2010_i686`
* `pywhlobf/pywhlobf:0.2.6-manylinux2014_x86_64`
* `pywhlobf/pywhlobf:0.2.6-manylinux2014_i686`

We also provide builds based on Cython 3.0 prerelease version:

* `pywhlobf/pywhlobf:0.2.6-cython3-manylinux_2_24_x86_64`
* `pywhlobf/pywhlobf:0.2.6-cython3-manylinux_2_24_i686`
* `pywhlobf/pywhlobf:0.2.6-cython3-manylinux1_x86_64`
* `pywhlobf/pywhlobf:0.2.6-cython3-manylinux1_i686`
* `pywhlobf/pywhlobf:0.2.6-cython3-manylinux2010_x86_64`
* `pywhlobf/pywhlobf:0.2.6-cython3-manylinux2010_i686`
* `pywhlobf/pywhlobf:0.2.6-cython3-manylinux2014_x86_64`
* `pywhlobf/pywhlobf:0.2.6-cython3-manylinux2014_i686`

To properly run the docker container, user should provide the following arguments to the `docker run` command:

* `-e PYTHON_ABI_TAG=<some_tag>`: required. Indicating the supported Python & ABI tag. Should be one of `cp37-cp37m`, `cp38-cp38`, `cp39-cp39`, `cp310-cp310`.
* `--user "$(id -u):$(id -g)"`: required. This field will be used by [boxboat/fixuid](https://github.com/boxboat/fixuid) to make sure the permission of output files are correct.
* `--rm -it`: optional but recommended. This options make sure the container is deleted on exit.

Example of usage:

```bash
# Show help doc.
docker run \
  --rm -it \
  --user "$(id -u):$(id -g)" \
  -e PYTHON_ABI_TAG=cp37-cp37m \
  pywhlobf/pywhlobf:0.2.6-manylinux2014_x86_64 \
  --help

<< OUTPUT
export HOME="/home/pywhlobf"
PYWHLOBF=/opt/python/cp37-cp37m/bin/pywhlobf
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
        Default: 'manylinux2014_x86_64'
        If set, hardcode the platform tag within the output wheel filename to this one.

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
OUTPUT

# Download wheel-0.36.2-py2.py3-none-any.whl.
curl \
  'https://files.pythonhosted.org/packages/65/63/39d04c74222770ed1589c0eaba06c05891801219272420b40311cd60c880/wheel-0.36.2-py2.py3-none-any.whl' \
  --output 'wheel-0.36.2-py2.py3-none-any.whl'

# Obfuscate wheel-0.36.2-py2.py3-none-any.whl
# NOTE: `-v "$(pwd)":/data` mounts the current working directory to /data within the container.
docker run \
  --rm -it \
  --user "$(id -u):$(id -g)" \
  -e PYTHON_ABI_TAG=cp37-cp37m \
  -v "$(pwd)":/data \
  pywhlobf/pywhlobf:0.2.6-manylinux2014_x86_64 \
  '/data/wheel-0.36.2-py2.py3-none-any.whl' \
  '/data/tmp'

<< OUTPUT
export HOME="/home/pywhlobf"
PYWHLOBF=/opt/python/cp37-cp37m/bin/pywhlobf
[INFO] Processing /data/wheel-0.36.2-py2.py3-none-any.whl...
[INFO] input_whl=/data/wheel-0.36.2-py2.py3-none-any.whl
[INFO] distribution=wheel, version=0.36.2, build_tag=None
[INFO] extract_folder=/tmp/tmpt_epivyo
[INFO] Build options: compiler_options=None, cythonize_options=None, processes=None
[INFO] Building 16 python files...
[INFO] The following source files are removed:
[INFO]   wheel/__main__.py
[INFO]   wheel/macosx_libfile.py
[INFO]   wheel/__init__.py
[INFO]   wheel/pkginfo.py
[INFO]   wheel/metadata.py
[INFO]   wheel/wheelfile.py
[INFO]   wheel/util.py
[INFO]   wheel/bdist_wheel.py
[INFO]   wheel/vendored/__init__.py
[INFO]   wheel/vendored/packaging/__init__.py
[INFO]   wheel/vendored/packaging/_typing.py
[INFO]   wheel/vendored/packaging/tags.py
[INFO]   wheel/cli/pack.py
[INFO]   wheel/cli/__init__.py
[INFO]   wheel/cli/convert.py
[INFO]   wheel/cli/unpack.py
[INFO] Repacking...
[INFO] output_whl_name=wheel-0.36.2-cp37-cp37m-manylinux2014_x86_64.whl
[INFO] output_whl=/data/tmp/wheel-0.36.2-cp37-cp37m-manylinux2014_x86_64.whl
[INFO] Done.
[INFO]
OUTPUT

cd tmp && ls -alh

<< OUTPUT
total 6416
drwxr-xr-x  3 huntzhan  staff    96B Feb 23 14:33 .
drwxr-xr-x  4 huntzhan  staff   128B Feb 23 14:33 ..
-rw-r--r--  1 huntzhan  staff   3.1M Feb 23 14:33 wheel-0.36.2-cp37-cp37m-manylinux2014_x86_64.whl
OUTPUT

unzip wheel-0.36.2-cp37-cp37m-manylinux2014_x86_64.whl

<< OUTPUT
Archive:  wheel-0.36.2-cp37-cp37m-manylinux2014_x86_64.whl
  inflating: wheel/__init__.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/__main__.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/bdist_wheel.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/macosx_libfile.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/metadata.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/pkginfo.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/util.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/wheelfile.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/cli/__init__.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/cli/convert.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/cli/pack.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/cli/unpack.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/vendored/__init__.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/vendored/packaging/__init__.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/vendored/packaging/_typing.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel/vendored/packaging/tags.cpython-36m-x86_64-linux-gnu.so
  inflating: wheel-0.36.2.dist-info/LICENSE.txt
  inflating: wheel-0.36.2.dist-info/METADATA
  inflating: wheel-0.36.2.dist-info/WHEEL
  inflating: wheel-0.36.2.dist-info/entry_points.txt
  inflating: wheel-0.36.2.dist-info/top_level.txt
  inflating: wheel-0.36.2.dist-info/RECORD
OUTPUT
```

### Install from PyPI

```bash
pip install pywhlobf
pywhlobf -- --help
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

