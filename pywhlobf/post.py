from itertools import chain
import iolite as io


def remove_source_files(input_folder):
    in_fd = io.folder(input_folder, exists=True)

    src_files = list(
        chain(
            # Python.
            in_fd.glob('**/*.py'),
            in_fd.glob('**/*.pyc'),
            # Cython.
            in_fd.glob('**/*.pyx'),
            in_fd.glob('**/*.pyd'),
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


def debug():
    import os
    pywhlobf_data = os.getenv('PYWHLOBF_DATA')
    assert pywhlobf_data

    src_files = remove_source_files(f'{pywhlobf_data}/prep/textwolf-0.9.0')
    print(src_files)
