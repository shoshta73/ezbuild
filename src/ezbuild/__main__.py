from importlib.metadata import version
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
    exit_code, message = commands.run(name=name)
    if exit_code != 0:
        log.error(message)
    raise typer.Exit(exit_code)


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
