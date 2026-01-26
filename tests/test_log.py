from typing import TYPE_CHECKING

from ezbuild.log import LogLevel, debug, error, info
from ezbuild.python_environment import PythonEnvironment

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_log_level_enum() -> None:
    assert LogLevel.DEBUG.name == "DEBUG"
    assert LogLevel.INFO.name == "INFO"
    assert LogLevel.ERROR.name == "ERROR"


def test_debug_calls_echo_when_enabled(mocker: MockerFixture) -> None:
    mocker.patch.object(PythonEnvironment, "_debug", True)
    mock_echo = mocker.patch("ezbuild.log.typer.echo")
    debug("test message")
    mock_echo.assert_called_once()
    call_arg = mock_echo.call_args[0][0]
    assert "DEBUG" in call_arg
    assert "test message" in call_arg


def test_debug_suppressed_when_disabled(mocker: MockerFixture) -> None:
    mocker.patch.object(PythonEnvironment, "_debug", False)
    mock_echo = mocker.patch("ezbuild.log.typer.echo")
    debug("test message")
    mock_echo.assert_not_called()


def test_info_calls_echo(mocker: MockerFixture) -> None:
    mock_echo = mocker.patch("ezbuild.log.typer.echo")
    info("test message")
    mock_echo.assert_called_once()
    call_arg = mock_echo.call_args[0][0]
    assert "INFO" in call_arg
    assert "test message" in call_arg


def test_error_calls_echo(mocker: MockerFixture) -> None:
    mock_echo = mocker.patch("ezbuild.log.typer.echo")
    error("test message")
    mock_echo.assert_called_once()
    call_arg = mock_echo.call_args[0][0]
    assert "ERROR" in call_arg
    assert "test message" in call_arg


def test_debug_output_when_enabled(mocker: MockerFixture, capsys) -> None:
    mocker.patch.object(PythonEnvironment, "_debug", True)
    debug("test message")
    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
    assert "test message" in captured.out


def test_debug_no_output_when_disabled(mocker: MockerFixture, capsys) -> None:
    mocker.patch.object(PythonEnvironment, "_debug", False)
    debug("test message")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_info_output(capsys) -> None:
    info("test message")
    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "test message" in captured.out


def test_error_output(capsys) -> None:
    error("test message")
    captured = capsys.readouterr()
    assert "ERROR" in captured.out
    assert "test message" in captured.out


def test_log_format_brackets(capsys) -> None:
    info("hello world")
    captured = capsys.readouterr()
    assert "[" in captured.out
    assert "]" in captured.out
