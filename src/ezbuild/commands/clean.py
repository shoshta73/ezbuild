from pathlib import Path
from shutil import rmtree

from ezbuild.log import info


def clean() -> None:
    """Clean the project."""
    cwd = Path.cwd()
    build_dir = cwd / "build"
    if not build_dir.exists():
        info("Nothing to clean")
        return

    info("Cleaning build directory")
    rmtree(build_dir)
    info("Cleaned build directory")
