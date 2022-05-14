from setuptools import setup, find_packages

try:
    from Cython.Build import cythonize
except ImportError:

    def cythonize(x, **kwargs):
        return None


__version__ = "0.69.5"


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
