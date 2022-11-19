import sys
from itertools import chain
import pathlib
from distutils.util import get_platform

from wheel.bdist_wheel import get_abi_tag
from wheel.wheelfile import WheelFile


def remove_source_files(input_folder):
    in_fd = pathlib.Path(input_folder)
    if not in_fd.is_dir():
        raise RuntimeError(f'input_folder={input_folder} is not a folder.')

    src_files = list(
        chain(
            # Python.
            in_fd.glob('**/*.py'),
            in_fd.glob('**/*.pyc'),
            # Cython.
            in_fd.glob('**/*.pyx'),
            # C/C++
            in_fd.glob('**/*.c'),
            in_fd.glob('**/*.C'),
            in_fd.glob('**/*.cc'),
            in_fd.glob('**/*.cpp'),
            in_fd.glob('**/*.cxx'),
            in_fd.glob('**/*.c++'),
            in_fd.glob('**/*.h'),
            in_fd.glob('**/*.H'),
            in_fd.glob('**/*.hh'),
            in_fd.glob('**/*.hpp'),
            in_fd.glob('**/*.hxx'),
            in_fd.glob('**/*.h++'),
        )
    )

    for src_file in src_files:
        src_file.unlink()

    return src_files


def generate_whl_name(
    input_folder,
    distribution,
    version,
    build_tag,
    abi_tag=None,
    platform_tag=None,
):
    python_tag = 'cp' + ''.join(map(str, sys.version_info[:2]))
    abi_tag = abi_tag or get_abi_tag()

    # https://peps.python.org/pep-0425/#platform-tag
    platform_tag = platform_tag or get_platform()
    platform_tag = platform_tag.replace('-', '_').replace('.', '_')

    components = [distribution, version]
    if build_tag:
        components.append(build_tag)
    components.extend([python_tag, abi_tag, platform_tag])

    return '-'.join(components) + '.whl'


def repack_whl(input_folder, output_whl):
    with WheelFile(output_whl, 'w') as wf:
        wf.write_files(input_folder)


def debug():
    import os
    pywhlobf_data = os.getenv('PYWHLOBF_DATA')
    assert pywhlobf_data

    src_files = remove_source_files(f'{pywhlobf_data}/prep/textwolf-0.9.0')
    print(src_files)

    whl_name = generate_whl_name(f'{pywhlobf_data}/prep/textwolf-0.9.0', 'textwolf', '0.9.0', None)
    print(whl_name)

    repack_whl(
        f'{pywhlobf_data}/prep/textwolf-0.9.0',
        f'{pywhlobf_data}/prep/{whl_name}',
    )
