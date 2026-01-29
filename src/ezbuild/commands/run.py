from pathlib import Path
from subprocess import run as sbp_run
from typing import Annotated

from typer import Argument

from ezbuild.commands.build import build
from ezbuild.log import debug


def run(
    name: Annotated[str, Argument(help="Name of the project to run")],
) -> tuple[int, str]:
    """Run the project."""

    cwd = Path.cwd()
    build_dir = cwd / "build"
    bin_dir = build_dir / "bin"

    if not (bin_dir / name).exists():
        exit_code, msg = build(name=name)
        if exit_code != 0:
            return 1, f"Failed to build project {name}: {msg}"

    cmd = f"{bin_dir / name}"
    debug(f"Running {cmd}")
    result = sbp_run([str(bin_dir / name)])
    if result.returncode != 0:
        stderr = result.stderr.decode() if result.stderr else ""
        return 2, f"Failed to run {cmd}: {stderr}"

    return 0, ""
