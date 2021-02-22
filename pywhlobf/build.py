import os
import sys
import tempfile
from distutils.core import setup
import shutil
import contextlib
from io import StringIO
import traceback
import multiprocessing
import pathlib

from Cython.Compiler import Options
from Cython.Compiler.Errors import CompileError
from Cython.Build.Dependencies import cythonize


def configure(compiler_options, cythonize_options):
    if compiler_options is None:
        # TODO: configure default compiler options.
        compiler_options = {}

    for key, val in compiler_options.items():
        setattr(Options, key, val)

    if cythonize_options is None:
        cythonize_options = {
            'language_level': 3,
        }

    return cythonize_options


def is_package_fd(fd):
    for name in ('__init__.py', '__init__.pyc', '__init__.pyx', '__init__.pxd'):
        if (fd / name).is_file():
            return True
    return False


def is_root_fd(fd):
    return fd.parent == fd


def build_py_file_inplace_output(
    py_file,
    status,
    compiler_stdout,
    compiler_stderr,
    cythonize_stdout,
    cythonize_stderr,
):
    return {
        'py_file': py_file,
        'status': status,
        'compiler_stdout': compiler_stdout,
        'compiler_stderr': compiler_stderr,
        'cythonize_stdout': cythonize_stdout,
        'cythonize_stderr': cythonize_stderr,
    }


def build_py_file_inplace(py_file, compiler_options, cythonize_options):
    cythonize_options = configure(
        compiler_options=compiler_options,
        cythonize_options=cythonize_options,
    )

    # Compile python file to c file.
    compiler_failed = False
    compiler_stdout = StringIO()
    compiler_stderr = StringIO()

    with contextlib.redirect_stdout(compiler_stdout), contextlib.redirect_stderr(compiler_stderr):
        try:
            ext_modules = cythonize(module_list=[str(py_file)], **cythonize_options)
        except CompileError:
            compiler_failed = True
            compiler_stderr.write('\nCatch CompileError:\n')
            compiler_stderr.write(traceback.format_exc())

    compiler_stdout = compiler_stdout.getvalue()
    compiler_stderr = compiler_stderr.getvalue()
    if compiler_failed:
        return build_py_file_inplace_output(
            py_file=py_file,
            status=False,
            compiler_stdout=compiler_stdout,
            compiler_stderr=compiler_stderr,
            cythonize_stdout='',
            cythonize_stderr='',
        )

    # Move to non-package parent.
    base_fd = py_file.parent
    while is_package_fd(base_fd) and not is_root_fd(base_fd):
        base_fd = base_fd.parent
    if is_root_fd(base_fd):
        return build_py_file_inplace_output(
            py_file=py_file,
            status=False,
            compiler_stdout=compiler_stdout,
            compiler_stderr=compiler_stderr,
            cythonize_stdout='',
            cythonize_stderr='Base folder reach root.',
        )
    os.chdir(base_fd)

    # Build c file.
    temp_fd = pathlib.Path(tempfile.mkdtemp(dir=base_fd))

    cythonize_failed = False
    cythonize_stdout = StringIO()

    # Redirect gcc/clang warning as well.
    stderr_fileno = os.dup(sys.stderr.fileno())
    redirected_stderr_file = open(temp_fd / 'cythonize_stderr.txt', 'w+')
    os.dup2(redirected_stderr_file.fileno(), sys.stderr.fileno())

    with contextlib.redirect_stdout(cythonize_stdout):
        try:
            setup(
                script_name='setup.py',
                script_args=[
                    'build_ext',
                    '-i',
                    '--build-temp',
                    str(temp_fd),
                ],
                ext_modules=ext_modules,
            )
        except Exception:
            cythonize_failed = True
            redirected_stderr_file.write('\nCatch Exception:\n')
            redirected_stderr_file.write(traceback.format_exc())

    # Load the redirected stderr.
    redirected_stderr_file.flush()
    redirected_stderr_file.seek(0)
    cythonize_stderr = redirected_stderr_file.read()
    redirected_stderr_file.close()

    # Restore stderr.
    os.dup2(stderr_fileno, sys.stderr.fileno())

    cythonize_stdout = cythonize_stdout.getvalue()
    if cythonize_failed:
        return build_py_file_inplace_output(
            py_file=py_file,
            status=False,
            compiler_stdout=compiler_stdout,
            compiler_stderr=compiler_stderr,
            cythonize_stdout=cythonize_stdout,
            cythonize_stderr=cythonize_stderr,
        )

    # Cleanup temp.
    shutil.rmtree(temp_fd)

    # Cleanup c file.
    c_file = py_file.with_suffix('.c')
    assert c_file.is_file()
    c_file.unlink()

    return build_py_file_inplace_output(
        py_file=py_file,
        status=True,
        compiler_stdout=compiler_stdout,
        compiler_stderr=compiler_stderr,
        cythonize_stdout=cythonize_stdout,
        cythonize_stderr=cythonize_stderr,
    )


def proc_build_py_file_inplace(args):
    py_file, compiler_options, cythonize_options = args
    return build_py_file_inplace(py_file, compiler_options, cythonize_options)


def build_py_files_inplace(
    py_files,
    compiler_options=None,
    cythonize_options=None,
    processes=None,
):
    with multiprocessing.Pool(processes=processes) as pool:
        inputs = [(py_file, compiler_options, cythonize_options) for py_file in py_files]
        results = pool.imap_unordered(proc_build_py_file_inplace, inputs)

        perfect_results = []
        warning_results = []
        error_results = []

        for result in results:
            if not result['status']:
                error_results.append(result)
            elif result['compiler_stderr'] or result['cythonize_stderr']:
                warning_results.append(result)
            else:
                perfect_results.append(result)

        return perfect_results, warning_results, error_results


def debug():
    import os
    pywhlobf_data = os.getenv('PYWHLOBF_DATA')
    assert pywhlobf_data

    from pywhlobf.prep import locate_py_files
    py_files = locate_py_files(f'{pywhlobf_data}/prep/textwolf-0.9.0')

    perfect_results, warning_results, error_results = build_py_files_inplace(py_files)
