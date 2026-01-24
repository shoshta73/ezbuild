from typing import TYPE_CHECKING

from ezbuild.python_environment import PythonEnvironment

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_debug_returns_bool() -> None:
    result = PythonEnvironment.debug()
    assert isinstance(result, bool)


def test_debug_default_value() -> None:
    assert PythonEnvironment._debug == __debug__


def test_debug_returns_class_attribute() -> None:
    assert PythonEnvironment.debug() == PythonEnvironment._debug


def test_debug_can_be_mocked(mocker: MockerFixture) -> None:
    mocker.patch.object(PythonEnvironment, "_debug", False)
    assert PythonEnvironment.debug() is False

    mocker.patch.object(PythonEnvironment, "_debug", True)
    assert PythonEnvironment.debug() is True
