import os
import subprocess
import sys
import textwrap

from setuptools import find_packages, setup

__version__ = "0.71.8"


def parse_setuppy_commands():
    """Check the commands and respond appropriately.  Disable broken commands.
    Return a boolean value for whether or not to run the build or not (avoid
    parsing Cython and template files if False).
    """
    args = sys.argv[1:]
    if not args:
        # User forgot to give an argument probably, let setuptools handle that.
        return True

    # fmt: off
    info_commands = ['--help-commands', '--name', '--version', '-V',
                     '--fullname', '--author', '--author-email',
                     '--maintainer', '--maintainer-email', '--contact',
                     '--contact-email', '--url', '--license', '--description',
                     '--long-description', '--platforms', '--classifiers',
                     '--keywords', '--provides', '--requires', '--obsoletes',
                     'version',]

    for command in info_commands:
        if command in args:
            return False

    # Note that 'alias', 'saveopts' and 'setopt' commands also seem to work
    # fine as they are, but are usually used together with one of the commands
    # below and not standalone.  Hence they're not added to good_commands.
    good_commands = ('develop', 'sdist', 'build', 'build_ext', 'build_py',
                     'build_clib', 'build_scripts', 'bdist_wheel', 'bdist_rpm',
                     'bdist_wininst', 'bdist_msi', 'bdist_mpkg', 'build_src',
                     'bdist_egg')

    for command in good_commands:
        if command in args:
            return True

    # The following commands are supported, but we need to show more
    # useful messages to the user
    if 'install' in args:
        print(textwrap.dedent("""
            Note: if you need reliable uninstall behavior, then install
            with pip instead of using `setup.py install`:
              - `pip install .`       (from a git repo or downloaded source
                                       release)
              - `pip install eudplib` (last eudplib release on PyPI)
            """))
        return True

    if '--help' in args or '-h' in sys.argv[1]:
        return False

    # The following commands aren't supported.  They can only be executed when
    # the user explicitly adds a --force command-line argument.
    bad_commands = dict(
        test="""
            `setup.py test` is not supported.  Use one of the following
            instead:
              - `python runtests.py`              (to build and test)
              - `python runtests.py --no-build`   (to test installed eudplib)
              - `>>> eudplib.test()`         (run tests for installed eudplib
                                              from within an interpreter)
            """,
        upload="""
            `setup.py upload` is not supported, because it's insecure.
            Instead, build what you want to upload and upload those files
            with `twine upload -s <filenames>` instead.
            """,
        clean="""
            `setup.py clean` is not supported, use one of the following instead:
              - `git clean -xdf` (cleans all files)
              - `git clean -Xdf` (cleans all versioned files, doesn't touch
                                  files that aren't checked into the git repo)
            """,
        build_sphinx="""
            `setup.py build_sphinx` is not supported, use the
            Makefile under doc/""",
        flake8="`setup.py flake8` is not supported, use flake8 standalone",
        )
    bad_commands['nosetests'] = bad_commands['test']
    for command in ('upload_docs', 'easy_install', 'bdist', 'bdist_dumb',
                    'register', 'check', 'install_data', 'install_headers',
                    'install_lib', 'install_scripts', ):
        bad_commands[command] = "`setup.py %s` is not supported" % command
    # fmt: on

    for command in bad_commands.keys():
        if command in args:
            print(
                textwrap.dedent(bad_commands[command])
                + "\nAdd `--force` to your command to use it anyway if you "
                "must (unsupported).\n"
            )
            sys.exit(1)

    # Commands that do more than print info, but also don't need Cython and
    # template parsing.
    other_commands = ["egg_info", "install_egg_info", "rotate", "dist_info"]
    for command in other_commands:
        if command in args:
            return False

    # If we got here, we didn't detect what setup.py command was given
    raise RuntimeError("Unrecognized setuptools command: {}".format(args))


def generate_cython():
    try:
        import Cython
    except ImportError as e:
        msg = "Cython needs to be installed in Python as a module"
        raise OSError(msg) from e

    cwd = os.path.abspath(os.path.dirname(__file__))
    print("Cythonizing sources")
    p = subprocess.call(
        [sys.executable, os.path.join(cwd, "tools", "cythonize.py"), "eudplib"],
        cwd=cwd,
    )
    if p != 0:
        raise RuntimeError("Running cythonize failed!")


if __name__ == "__main__":
    src_path = os.path.dirname(os.path.abspath(__file__))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    if "--force" in sys.argv:
        run_build = True
        sys.argv.remove("--force")
    else:
        # Raise errors for unsupported commands, improve help output, etc.
        run_build = parse_setuppy_commands()

    if run_build:
        if "sdist" not in sys.argv:
            # Generate Cython sources, unless we're generating an sdist
            generate_cython()

    try:
        from Cython.Build import cythonize

        setup(
            name="eudplib",
            version=__version__,
            packages=find_packages(),
            package_data={"": ["*.c", "*.pyx", "*.dll", "*.dylib", "*.lst", "*.mo"]},
            include_package_data=True,
            ext_modules=cythonize(["eudplib/**/*.pyx"], language_level="3"),
            python_requires=">=3.10",
            # metadata for upload to PyPI
            author="Trgk",
            author_email="whyask37@naver.com",
            maintainer="Armoha",
            maintainer_email="kein0011@naver.com",
            description="EUD Trigger generator",
            license="MIT license",
            keywords="starcraft rawtrigger eud",
            url="https://github.com/armoha/eudplib",  # project home page, if any
        )
    finally:
        del sys.path[0]
        os.chdir(old_path)
