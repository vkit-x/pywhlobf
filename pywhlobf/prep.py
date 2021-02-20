import zipfile
import iolite as io


def unzip_wheel(input_whl, output_folder):
    out_fd = io.folder(output_folder, reset=True)
    with zipfile.ZipFile(input_whl) as zip_file:
        zip_file.extractall(out_fd)


def locate_py_files(input_folder):
    in_fd = io.folder(input_folder, exists=True)
    return list(in_fd.glob('**/*.py'))


def debug():
    import os
    pywhlobf_data = os.getenv('PYWHLOBF_DATA')
    assert pywhlobf_data

    unzip_wheel(
        f'{pywhlobf_data}/prep/textwolf-0.9.0-py3-none-any.whl',
        f'{pywhlobf_data}/prep/textwolf-0.9.0',
    )

    py_files = locate_py_files(f'{pywhlobf_data}/prep/textwolf-0.9.0')
    print(py_files)
