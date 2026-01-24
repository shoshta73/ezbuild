from enum import Enum, auto

import typer

from ezbuild.python_environment import PythonEnvironment


class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    ERROR = auto()


def debug(message: str) -> None:
    if PythonEnvironment.debug():
        return

    typer.echo(f"[{typer.style(LogLevel.DEBUG.name, fg=typer.colors.CYAN)}] {message}")


def info(message: str) -> None:
    typer.echo(f"[{typer.style(LogLevel.INFO.name, fg=typer.colors.GREEN)}] {message}")


def error(message: str) -> None:
    typer.echo(f"[{typer.style(LogLevel.ERROR.name, fg=typer.colors.RED)}] {message}")


def cc(message: str) -> None:
    typer.echo(f"[{typer.style('CC', fg=typer.colors.CYAN)}] {message}")


def cxx(message: str) -> None:
    typer.echo(f"[{typer.style('CXX', fg=typer.colors.CYAN)}] {message}")


def ccld(message: str) -> None:
    typer.echo(f"[{typer.style('CCLD', fg=typer.colors.CYAN)}] {message}")


def cxxld(message: str) -> None:
    typer.echo(f"[{typer.style('CXXLD', fg=typer.colors.CYAN)}] {message}")


def ar(message: str) -> None:
    typer.echo(f"[{typer.style('AR', fg=typer.colors.CYAN)}] {message}")


def ranlib(message: str) -> None:
    typer.echo(f"[{typer.style('RANLIB', fg=typer.colors.CYAN)}] {message}")
