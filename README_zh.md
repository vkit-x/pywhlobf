[English](README.md) | 简体中文

# pywhlobf

## 简介

pywhlobf 是一个 Python 代码混淆工具，输入一个 [wheel 格式分发包](https://www.python.org/dev/peps/pep-0427/) (也就是说，您首先得执行如 `python -m build --wheel` 的命令将项目打成 wheel 包，然后才能使用本工具)，输出一个混淆后的 wheel 包，包中所有的 `.py` Python 文件将会编译替换为目标平台的二进制文件，从而达到混淆/保护代码的目的。

## 使用方式

### 使用基于 `manylinux` 的 Docker 镜像

下列镜像基于 [pypa/manylinux](https://github.com/pypa/manylinux) 提供的基础镜像构建，镜像的标签格式为 `<pywhlobf_version>-<platform_tag>`。完整的镜像列表见 [pywhlobf/tags](https://hub.docker.com/r/pywhlobf/pywhlobf/tags)。如果您的运行环境不属于下列平台（如希望混淆后的包可以在 macOS 或 Windows 上执行），您需要在目标运行环境手动从 PyPI 安装 `pywhlobf`，具体见下一小节。

* `pywhlobf/pywhlobf:22.1.0-manylinux1_x86_64`
* `pywhlobf/pywhlobf:22.1.0-manylinux1_i686`
* `pywhlobf/pywhlobf:22.1.0-manylinux2010_x86_64`
* `pywhlobf/pywhlobf:22.1.0-manylinux2010_i686`
* `pywhlobf/pywhlobf:22.1.0-manylinux2014_x86_64`
* `pywhlobf/pywhlobf:22.1.0-manylinux2014_i686`
* `pywhlobf/pywhlobf:22.1.0-manylinux_2_24_x86_64`
* `pywhlobf/pywhlobf:22.1.0-manylinux_2_24_i686`

同时我们也提供基于 Cython 3.0 prerelease 版本的镜像：

* `pywhlobf/pywhlobf:22.1.0-cython3-manylinux1_x86_64`
* `pywhlobf/pywhlobf:22.1.0-cython3-manylinux1_i686`
* `pywhlobf/pywhlobf:22.1.0-cython3-manylinux2010_x86_64`
* `pywhlobf/pywhlobf:22.1.0-cython3-manylinux2010_i686`
* `pywhlobf/pywhlobf:22.1.0-cython3-manylinux2014_x86_64`
* `pywhlobf/pywhlobf:22.1.0-cython3-manylinux2014_i686`
* `pywhlobf/pywhlobf:22.1.0-cython3-manylinux_2_24_x86_64`
* `pywhlobf/pywhlobf:22.1.0-cython3-manylinux_2_24_i686`

由于某些懂得都懂的原因，在中国大陆地区从 Docker Hub 拉镜像是非常慢的。我们非常贴心地为您提供了镜像版本。为了加速，可以在拉取镜像时在镜像名前面加上 `swr.cn-east-3.myhuaweicloud.com/` 前缀，如 `docker pull swr.cn-east-3.myhuaweicloud.com/pywhlobf/pywhlobf:22.1.0-manylinux2014_x86_64`，然后执行 `docker tag swr.cn-east-3.myhuaweicloud.com/pywhlobf/pywhlobf:22.1.0-manylinux2014_x86_64 pywhlobf/pywhlobf:22.1.0-manylinux2014_x86_64`。

为了合理使用我们提供的镜像，您需要在执行 `docker run` 时提供如下参数：

* `-e PYTHON_ABI_TAG=<some_tag>`：必须提供。这个用于表示目标执行环境的 Python 版本与 ABI 标签。目前支持 `cp36-cp36m`, `cp37-cp37m`, `cp38-cp38`, `cp39-cp39`, `cp310-cp310`, `cp311-cp311`。
* `--user "$(id -u):$(id -g)"`：必须提供。 [boxboat/fixuid](https://github.com/boxboat/fixuid) 会基于这个字段保证混淆后的文件的权限的正确性。
* `--rm -it`：不必要但推荐使用。这个选项会保证容器会在退出后被自动删除。

使用样例:

```bash
# 输出帮助文档。
docker run \
  --rm -it \
  --user "$(id -u):$(id -g)" \
  -e PYTHON_ABI_TAG=cp36-cp36m \
  pywhlobf/pywhlobf:22.1.0-manylinux2014_x86_64 \
  --help

<< OUTPUT
export HOME="/home/pywhlobf"
PYWHLOBF=/opt/python/cp36-cp36m/bin/pywhlobf
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

# 下载 wheel-0.36.2-py2.py3-none-any.whl。
curl \
  'https://files.pythonhosted.org/packages/65/63/39d04c74222770ed1589c0eaba06c05891801219272420b40311cd60c880/wheel-0.36.2-py2.py3-none-any.whl' \
  --output 'wheel-0.36.2-py2.py3-none-any.whl'

# 混淆 wheel-0.36.2-py2.py3-none-any.whl
# 注意：`-v "$(pwd)":/data` 会挂载当前工作路径至容器中的 /data 路径。
docker run \
  --rm -it \
  --user "$(id -u):$(id -g)" \
  -e PYTHON_ABI_TAG=cp36-cp36m \
  -v "$(pwd)":/data \
  pywhlobf/pywhlobf:22.1.0-manylinux2014_x86_64 \
  '/data/wheel-0.36.2-py2.py3-none-any.whl' \
  '/data/tmp'

<< OUTPUT
export HOME="/home/pywhlobf"
PYWHLOBF=/opt/python/cp36-cp36m/bin/pywhlobf
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
[INFO] output_whl_name=wheel-0.36.2-cp36-cp36m-manylinux2014_x86_64.whl
[INFO] output_whl=/data/tmp/wheel-0.36.2-cp36-cp36m-manylinux2014_x86_64.whl
[INFO] Done.
[INFO]
OUTPUT

cd tmp && ls -alh

<< OUTPUT
total 6416
drwxr-xr-x  3 huntzhan  staff    96B Feb 23 14:33 .
drwxr-xr-x  4 huntzhan  staff   128B Feb 23 14:33 ..
-rw-r--r--  1 huntzhan  staff   3.1M Feb 23 14:33 wheel-0.36.2-cp36-cp36m-manylinux2014_x86_64.whl
OUTPUT

unzip wheel-0.36.2-cp36-cp36m-manylinux2014_x86_64.whl

<< OUTPUT
Archive:  wheel-0.36.2-cp36-cp36m-manylinux2014_x86_64.whl
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

### 从 PyPI 安装

```bash
pip install pywhlobf

# 或者，基于 Cython 3.0 prerelease
pip install 'pywhlobf[cython3]'

pywhlobf -- --help
```

例子:

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

