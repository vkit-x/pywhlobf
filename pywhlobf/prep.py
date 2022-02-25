import zipfile
import pathlib
import shutil
import os


def extract_tags(input_whl):
    input_whl = pathlib.Path(input_whl)
    if not input_whl.is_file():
        raise RuntimeError(f'{input_whl} is not a file.')
    if input_whl.suffix != '.whl':
        raise RuntimeError(f'{input_whl} does not ends with ".whl".')

    # https://www.python.org/dev/peps/pep-0427/
    name = input_whl.stem
    components = name.split('-')
    build_tag = None
    if len(components) == 5:
        distribution, version, _, _, _ = components
    elif len(components) == 6:
        distribution, version, build_tag, _, _, _ = components
    else:
        raise NotImplementedError()

    return distribution, version, build_tag


def unzip_wheel(input_whl, output_folder):
    out_fd = pathlib.Path(output_folder)
    if out_fd.is_file():
        raise RuntimeError(f'output_folder={output_folder} is a file')
    if out_fd.is_dir():
        shutil.rmtree(out_fd)
    os.makedirs(out_fd)

    with zipfile.ZipFile(input_whl) as zip_file:
        zip_file.extractall(out_fd)


def locate_py_files(input_folder):
    in_fd = pathlib.Path(input_folder)
    if not in_fd.is_dir():
        raise RuntimeError(f'input_folder={input_folder} is not a folder.')

    return list(in_fd.glob('**/*.py'))


def debug():
    import os
    pywhlobf_data = os.getenv('PYWHLOBF_DATA')
    assert pywhlobf_data

    print(extract_tags(f'{pywhlobf_data}/prep/textwolf-0.9.0-py3-none-any.whl'))

    unzip_wheel(
        f'{pywhlobf_data}/prep/textwolf-0.9.0-py3-none-any.whl',
        f'{pywhlobf_data}/prep/textwolf-0.9.0',
    )

    py_files = locate_py_files(f'{pywhlobf_data}/prep/textwolf-0.9.0')
    print(py_files)
