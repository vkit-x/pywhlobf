import logging
import tempfile
import sys
import shutil

import iolite as io
import fire

from pywhlobf.prep import extract_tags, unzip_wheel, locate_py_files
from pywhlobf.build import build_py_files_inplace
from pywhlobf.post import remove_source_files, generate_whl_name, repack_whl

logging.basicConfig(format='[%(levelname)s] %(message)s', level='INFO')
logger = logging.getLogger(__name__)


def run(
    input_whl,
    output_folder,
    temp_folder=None,
    compiler_options=None,
    cythonize_options=None,
    processes=None,
    show_warning=False,
    abi_tag=None,
    platform_tag=None,
):
    # Prep.
    logger.info(f'input_whl={input_whl}')

    distribution, version, build_tag = extract_tags(input_whl)
    logger.info(f'distribution={distribution}, version={version}, build_tag={build_tag}')

    temp_root_fd = None
    if temp_folder:
        temp_root_fd = io.folder(temp_folder, touch=True)

    extract_folder = tempfile.mkdtemp(dir=temp_root_fd)
    logger.info(f'extract_folder={extract_folder}')

    unzip_wheel(input_whl, extract_folder)

    py_files = locate_py_files(extract_folder)

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
            logger.error('-' * 20)
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

    out_fd = io.folder(output_folder, touch=True)
    output_whl = out_fd / output_whl_name
    logger.info(f'output_whl={output_whl}')

    repack_whl(extract_folder, output_whl)
    logger.info('Done.')

    shutil.rmtree(extract_folder)
    sys.exit(0)


fire_run = fire.Fire(run)
