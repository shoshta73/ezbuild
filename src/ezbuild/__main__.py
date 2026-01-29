import subprocess
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer

from ezbuild import (
    commands,
    log,
)

cli: typer.Typer = typer.Typer()


def version_callback(value: bool) -> None:
    if value:
        print(f"ezbuild {version('ezbuild')}")
        raise typer.Exit


@cli.command()
def init(
    language: Annotated[
        str | None, typer.Option("--language", "-l", help="Language which is used")
    ] = None,
    name: Annotated[
        str | None, typer.Argument(help="Name of the project to initialize")
    ] = None,
) -> None:
    """Initialize a new project."""
    exit_code, message = commands.init(language=language, name=name)
    if exit_code != 0:
        log.error(message)
    raise typer.Exit(exit_code)


@cli.command()
def build(
    name: Annotated[
        str | None, typer.Argument(help="Name of the project to build")
    ] = None,
) -> None:
    """Build the project."""
    exit_code, message = commands.build(name=name)
    if exit_code != 0:
        log.error(message)
    raise typer.Exit(exit_code)


@cli.command()
def run(
    name: Annotated[str, typer.Argument(help="Name of the project to initialize")],
) -> None:
    """Run the project."""
    cwd = Path.cwd()
    build_dir = cwd / "build"
    bin_dir = build_dir / "bin"

    if not (bin_dir / name).exists():
        build(name=name)

    cmd = f"{bin_dir / name}"
    log.debug(f"Running {cmd}")
    result = subprocess.run([str(bin_dir / name)])

    if result.returncode != 0:
        log.error("Running failed")
        log.debug(f"Error: {result.stderr.decode()}")
        raise typer.Exit


@cli.command()
def clean():
    """Clean the project."""
    commands.clean()


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = False,
) -> None:
    """Simple Build System."""
    if ctx.invoked_subcommand is None:
        build()


if __name__ == "__main__":
    cli()
