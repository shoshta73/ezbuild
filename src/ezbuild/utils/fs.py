from typing import TYPE_CHECKING

from ezbuild.log import debug, info

if TYPE_CHECKING:
    from pathlib import Path


def create_dir_if_not_exists(path: Path) -> None:
    debug(f"Checking if {path} exists")
    if not path.exists():
        debug(f"Creating {path}")
        path.mkdir()
        info(f"Created {path}")
    else:
        debug(f"{path} already exists")
