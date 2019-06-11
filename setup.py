from setuptools import setup, find_packages

try:
    from Cython.Build import cythonize
except ImportError:

    def cythonize(x):
        return None


__version__ = "0.59.0"


setup(
    name="eudplib",
    version=__version__,
    packages=find_packages(),
    package_data={"": ["*.c", "*.pyx", "*.dll", "*.dylib", "*.lst"]},
    ext_modules=cythonize(["eudplib/**/*.pyx"]),
    python_requires=">=3",
    # metadata for upload to PyPI
    author="Trgk",
    author_email="whyask37@naver.com",
    description="EUD Trigger generator",
    license="MIT license",
    keywords="starcraft rawtrigger eud",
    url="https://github.com/armoha/eudplib",  # project home page, if any
)
