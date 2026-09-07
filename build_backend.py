"""PEP 517 backend that builds the epScript C library, then delegates to maturin.

Builds ``libepScriptLib`` for the current platform (see
``src/epscript/build_epscript.py``) before maturin packages the wheel, so each
platform's wheel contains the matching dynamic library.

Also compiles .po files to .mo files for localization support.
"""

import glob
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


def _compile_locale() -> None:
    """Compile .po files to .mo files for all locales."""
    root = Path(__file__).parent
    po_files = glob.glob(
        str(root / "src" / "eudplib" / "localize" / "**" / "*.po"),
        recursive=True,
    )
    for po_path in po_files:
        mo_path = Path(po_path).with_suffix(".mo")
        try:
            subprocess.run(
                [sys.executable, "-m", "babel.messages.frontend", "compile",
                 "-i", po_path, "-o", str(mo_path)],
                check=True,
                capture_output=True,
            )
        except FileNotFoundError:
            print(
                f"Warning: babel not found, skipping compilation of {po_path}",
                file=sys.stderr,
            )
            return
        except subprocess.CalledProcessError as e:
            print(
                f"Warning: failed to compile {po_path}: {e.stderr}",
                file=sys.stderr,
            )


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    _build_epscript()
    _compile_locale()
    return _build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory, config_settings=None):
    # The sdist contains the sources; the library is built when the wheel is
    # built from it. `sdist-generator = "cargo"` excludes generated files.
    return _build_sdist(sdist_directory, config_settings)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    _build_epscript()
    _compile_locale()
    return _build_editable(wheel_directory, config_settings, metadata_directory)
