import logging
import tempfile
import sys
import shutil
import os
import pathlib

import fire

from pywhlobf.prep import extract_tags, unzip_wheel, locate_py_files
from pywhlobf.build import build_py_files_inplace
from pywhlobf.post import remove_source_files, generate_whl_name, repack_whl

logging.basicConfig(format='[%(levelname)s] %(message)s', level='INFO')
logger = logging.getLogger(__name__)

PYWHLOBF_ABI_TAG = os.getenv('PYWHLOBF_ABI_TAG')
PYWHLOBF_PLATFORM_TAG = os.getenv('PYWHLOBF_PLATFORM_TAG')


def run(
    input_whl,
    output_folder,
    temp_folder,
    compiler_options,
    cythonize_options,
    processes,
    show_warning,
    abi_tag,
    platform_tag,
):
    # Prep.
    logger.info(f'input_whl={input_whl}')

    distribution, version, build_tag = extract_tags(input_whl)
    logger.info(f'distribution={distribution}, version={version}, build_tag={build_tag}')

    temp_root_fd = None
    if temp_folder:
        temp_root_fd = pathlib.Path(temp_folder)
        if temp_root_fd.is_file():
            logger.error(f'temp_folder={temp_folder} is a file.')
            sys.exit(1)
        os.makedirs(temp_root_fd, exist_ok=True)

    extract_folder = tempfile.mkdtemp(dir=temp_root_fd)
    logger.info(f'extract_folder={extract_folder}')

    unzip_wheel(input_whl, extract_folder)

    py_files = locate_py_files(extract_folder)
    if not py_files:
        logger.info('No python file to build, abort.')
        return

    # Build.
    logger.info(
        'Build options: '
        f'compiler_options={compiler_options}, '
        f'cythonize_options={cythonize_options}, '
        f'processes={processes}'
    )
    logger.info(f'Building {len(py_files)} python files...')
    _, warning_results, error_results = build_py_files_inplace(
        py_files,
        compiler_options=compiler_options,
        cythonize_options=cythonize_options,
        processes=processes,
    )

    if show_warning and warning_results:
        logger.warning('WARNINGS:')
        for result in warning_results:
            py_file = result['py_file']
            compiler_stderr = result['compiler_stderr']
            cythonize_stderr = result['cythonize_stderr']
            logger.warning(f'py_file={py_file}')
            if compiler_stderr:
                logger.warning(f'compiler_stderr={compiler_stderr}')
            if cythonize_stderr:
                logger.warning(f'cythonize_stderr={cythonize_stderr}')
            logger.warning('-' * 20)

    if error_results:
        logger.error('ERRORS:')
        for result in error_results:
            py_file = result['py_file']
            compiler_stderr = result['compiler_stderr']
            cythonize_stderr = result['cythonize_stderr']
            logger.error(f'py_file={py_file}')
            if compiler_stderr:
                logger.error(f'compiler_stderr={compiler_stderr}')
            if cythonize_stderr:
                logger.error(f'cythonize_stderr={cythonize_stderr}')
            logger.error('-' * 60)
        logger.error('Failed to build, abort.')
        sys.exit(1)

    # Post.
    removed_src_files = remove_source_files(extract_folder)
    logger.info('The following source files are removed:')
    for src_file in removed_src_files:
        show_src_file = src_file.relative_to(extract_folder)
        logger.info(f'  {show_src_file}')

    logger.info('Repacking...')

    output_whl_name = generate_whl_name(
        extract_folder,
        distribution,
        version,
        build_tag,
        abi_tag=abi_tag,
        platform_tag=platform_tag,
    )
    logger.info(f'output_whl_name={output_whl_name}')

    out_fd = pathlib.Path(output_folder)
    if out_fd.is_file():
        logger.error(f'output_folder={output_folder} is a file.')
        sys.exit(1)
    os.makedirs(out_fd, exist_ok=True)

    output_whl = out_fd / output_whl_name
    logger.info(f'output_whl={output_whl}')

    if output_whl.is_dir():
        logger.warning(f'output_whl={output_whl} is a folder, removing...')
        shutil.rmtree(output_whl)
    elif output_whl.is_file():
        logger.warning(f'output_whl={output_whl} exists, overwriting...')

    repack_whl(extract_folder, output_whl)
    logger.info('Done.')

    shutil.rmtree(extract_folder)


def batch_run(
    input_whl_or_folder,
    output_folder,
    temp_folder=None,
    compiler_options=None,
    cythonize_options=None,
    processes=None,
    show_warning=False,
    abi_tag=PYWHLOBF_ABI_TAG,
    platform_tag=PYWHLOBF_PLATFORM_TAG,
):
    '''
    :param input_whl_or_folder:
        Path to the input wheel file, or the folder containing wheel file(s).
    :param output_folder:
        Path to the output folder.
    :param temp_folder:
        Path to the root of temporary folder.
    :param compiler_options:
        If provided, should be a dict containing only the supported keys
        of `Cython.Compiler.Options`, as shown in
        `https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-options`.
        Example: --compiler_options='{"docstrings": False}'
    :param cythonize_options:
        If provided, should be a dict containing only the supported parameters
        of `Cython.Build.cythonize, as shown in
        `https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#Cython.Build.cythonize`
        and
        `https://github.com/cython/cython/blob/9a761a637fce6a7b70735ae2248963d63e569e14/Cython/Compiler/Options.py#L566`
        Example: --cythonize_options='{"compiler_directives": {"emit_code_comments": False}}'
    :param processes:
        The number of worker processes to use. All CPUs are used by default.
    :param show_warning:
        If set, show the build warnings.
    :param abi_tag:
        If set, hardcode the ABI tag within the output wheel filename to this one.
    :param platform_tag:
        If set, hardcode the platform tag within the output wheel filename to this one.
    '''
    input_path = pathlib.Path(input_whl_or_folder)
    if not input_path.exists():
        logger.error(f'input_whl_or_folder={input_whl_or_folder} doesn\'t exist.')
        sys.exit(1)

    if input_path.is_file():
        input_whls = [input_path]
    elif input_path.is_dir():
        input_whls = list(input_path.glob('**/*.whl'))
    else:
        logger.error(f'input_whl_or_folder={input_whl_or_folder} is neither a file nor a folder.')
        sys.exit(1)

    for input_whl in input_whls:
        logger.info(f'Processing {input_whl}...')
        run(
            input_whl=input_whl,
            output_folder=output_folder,
            temp_folder=temp_folder,
            compiler_options=compiler_options,
            cythonize_options=cythonize_options,
            processes=processes,
            show_warning=show_warning,
            abi_tag=abi_tag,
            platform_tag=platform_tag,
        )
        logger.info('')

    sys.exit(0)


def fire_batch_run():
    fire.Fire(batch_run)
