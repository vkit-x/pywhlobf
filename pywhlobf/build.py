import os
import sys
import tempfile
from distutils.core import setup
import shutil
import contextlib
from io import StringIO
import traceback
import concurrent.futures
import pathlib
import re
import logging

from Cython.Compiler import Options
from Cython.Compiler.Errors import CompileError
from Cython.Build.Dependencies import cythonize

logger = logging.getLogger(__name__)


def configure(compiler_options, cythonize_options):
    if compiler_options is None:
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
    base_fd = py_file.parent
    temp_fd = pathlib.Path(tempfile.mkdtemp(dir=base_fd))

    cythonize_options = configure(
        compiler_options=compiler_options,
        cythonize_options=cythonize_options,
    )

    # Compile python file to c file.
    ext_modules = None

    compiler_failed = False
    compiler_stdout = StringIO()
    compiler_stderr = StringIO()
    with contextlib.redirect_stdout(compiler_stdout), contextlib.redirect_stderr(compiler_stderr):
        # Backup py_file.
        backup_py_file = temp_fd / py_file.name
        backup_py_file.write_bytes(py_file.read_bytes())

        # Inject py_file.
        code = py_file.read_bytes()
        py_file.write_bytes(b'# distutils: language=c++\n' + code)

        # Codegen.
        try:
            ext_modules = cythonize(module_list=[str(py_file)], **cythonize_options)
            assert ext_modules is not None
            assert len(ext_modules) == 1
        except CompileError:
            compiler_failed = True
            compiler_stderr.write('\nCatch CompileError:\n')
            compiler_stderr.write(traceback.format_exc())

    compiler_stdout_p1 = compiler_stdout.getvalue()
    compiler_stderr_p1 = compiler_stderr.getvalue()
    if compiler_failed:
        return build_py_file_inplace_output(
            py_file=py_file,
            status=False,
            compiler_stdout=compiler_stdout_p1,
            compiler_stderr=compiler_stderr_p1,
            cythonize_stdout='',
            cythonize_stderr='',
        )

    compiler_failed = False
    compiler_stdout = StringIO()
    compiler_stderr = StringIO()
    with contextlib.redirect_stdout(compiler_stdout), contextlib.redirect_stderr(compiler_stderr):
        # Copy obfuscate.h.
        include_fd = temp_fd / 'include'
        include_fd.mkdir()
        asset_fd = pathlib.Path(__file__).parent / 'asset'
        assert asset_fd.is_dir()
        for header_file in asset_fd.glob('*.h'):
            (include_fd / header_file.name).write_bytes(header_file.read_bytes())

        # Configure compiler.
        assert ext_modules is not None
        ext_module = ext_modules[0]
        ext_module.include_dirs = [str(include_fd)]
        ext_module.extra_compile_args = ['-std=c++14']

        # Inject obfuscate.h and obsucate string literals.
        cpp_file = py_file.parent / f'{py_file.stem}.cpp'
        assert cpp_file.is_file()
        code = cpp_file.read_text()

        # Pattern 1.
        pattern = r'^static const char (\w+)\[\] = \"(.*?)\";$'

        var_names = []
        for var_name, _ in re.findall(pattern, code, flags=re.MULTILINE):
            var_names.append(var_name)

        code = re.sub(
            pattern,
            '\n'.join([
                r'static const char *\1 = AY_OBFUSCATE("\2");',
                r'static const long __length\1 = HACK_LENGTH("\2");',
            ]),
            code,
            flags=re.MULTILINE,
        )
        for var_name in var_names:
            sizeof_pattern = r'sizeof\(' + var_name + r'\)'
            code = re.sub(sizeof_pattern, f'__length{var_name}', code)

        # Pattern 2.
        pattern = r'^static char (\w+)\[\] = \"(.*?)\";$'

        var_names = []
        for var_name, _ in re.findall(pattern, code, flags=re.MULTILINE):
            var_names.append(var_name)

        code = re.sub(
            pattern,
            '\n'.join([
                r'static char *\1 = AY_OBFUSCATE("\2");',
                r'static const long __length\1 = HACK_LENGTH("\2");',
            ]),
            code,
            flags=re.MULTILINE,
        )
        for var_name in var_names:
            sizeof_pattern = r'sizeof\(' + var_name + r'\)'
            code = re.sub(sizeof_pattern, f'__length{var_name}', code)

        cpp_file.write_text(
            '\n'.join([
                '#include "obfuscate.h"',
                '#include "obfuscate_sizeof.h"',
                code,
            ])
        )

        # Restore py_file.
        py_file.write_bytes(backup_py_file.read_bytes())

    compiler_stdout_p2 = compiler_stdout.getvalue()
    compiler_stderr_p2 = compiler_stderr.getvalue()

    compiler_stdout_all = '\n'.join([compiler_stdout_p1, compiler_stdout_p2])
    compiler_stderr_all = '\n'.join([compiler_stderr_p1, compiler_stderr_p2])

    if compiler_failed:
        return build_py_file_inplace_output(
            py_file=py_file,
            status=False,
            compiler_stdout=compiler_stdout_all,
            compiler_stderr=compiler_stderr_all,
            cythonize_stdout='',
            cythonize_stderr='',
        )

    # Move to non-package parent.
    while is_package_fd(base_fd) and not is_root_fd(base_fd):
        base_fd = base_fd.parent
    if is_root_fd(base_fd):
        return build_py_file_inplace_output(
            py_file=py_file,
            status=False,
            compiler_stdout=compiler_stdout_all,
            compiler_stderr=compiler_stderr_all,
            cythonize_stdout='',
            cythonize_stderr='Base folder reach root.',
        )
    os.chdir(base_fd)

    # Build c file.
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
            compiler_stdout=compiler_stdout_all,
            compiler_stderr=compiler_stderr_all,
            cythonize_stdout=cythonize_stdout,
            cythonize_stderr=cythonize_stderr,
        )

    # Cleanup temp.
    shutil.rmtree(temp_fd)

    # Cleanup C/C++ file.
    for ext in ['.c', '.cpp']:
        c_or_cpp_file = py_file.with_suffix(ext)
        if c_or_cpp_file.exists():
            assert c_or_cpp_file.is_file()
            c_or_cpp_file.unlink()

    return build_py_file_inplace_output(
        py_file=py_file,
        status=True,
        compiler_stdout=compiler_stdout_all,
        compiler_stderr=compiler_stderr_all,
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
    with concurrent.futures.ProcessPoolExecutor(max_workers=processes) as executor:
        inputs = [(py_file, compiler_options, cythonize_options) for py_file in py_files]
        results = executor.map(proc_build_py_file_inplace, inputs)

        perfect_results = []
        warning_results = []
        error_results = []

        for idx, result in enumerate(results):
            logger.info(f'{idx + 1}/{len(py_files)} obfuscated.')

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

    import iolite as io
    py_files = [io.file(f'{pywhlobf_data}/build/foo.py')]

    build_py_files_inplace(py_files)

    # ret = build_py_file_inplace(py_files[0], None, None)
    # print(ret['compiler_stdout'])
    # print(ret['cythonize_stdout'])
    # print(ret['cythonize_stderr'])
