"""PEP 517 backend that builds the epScript C library, then delegates to maturin.

Builds ``libepScriptLib`` for the current platform (see
``src/epscript/build_epscript.py``) before maturin packages the wheel, so each
platform's wheel contains the matching dynamic library.
"""

import os
import subprocess
import sys
from pathlib import Path

from maturin import (
    build_editable as _build_editable,
)
from maturin import (
    build_sdist as _build_sdist,
)
from maturin import (
    build_wheel as _build_wheel,
)
from maturin import (
    get_requires_for_build_editable,  # noqa: F401 (PEP 517 hook)
    get_requires_for_build_sdist,  # noqa: F401 (PEP 517 hook)
    get_requires_for_build_wheel,  # noqa: F401 (PEP 517 hook)
    prepare_metadata_for_build_editable,  # noqa: F401 (PEP 517 hook)
    prepare_metadata_for_build_wheel,  # noqa: F401 (PEP 517 hook)
)


def _build_epscript() -> None:
    root = Path(__file__).parent
    script = root / "src" / "epscript" / "build_epscript.py"
    env = {**os.environ}
    subprocess.run([sys.executable, str(script)], cwd=root, check=True, env=env)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    _build_epscript()
    return _build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory, config_settings=None):
    # The sdist contains the sources; the library is built when the wheel is
    # built from it. `sdist-generator = "cargo"` excludes generated files.
    return _build_sdist(sdist_directory, config_settings)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    _build_epscript()
    return _build_editable(wheel_directory, config_settings, metadata_directory)
