from typing import TYPE_CHECKING

import pytest
from typer import Exit

from ezbuild.environment import Environment, Program
from ezbuild.language import Language

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_program_creation() -> None:
    program = Program(name="myapp", languages=[Language.C], sources=["main.c"])
    assert program.name == "myapp"
    assert program.languages == [Language.C]
    assert program.sources == ["main.c"]


def test_program_multiple_sources() -> None:
    program = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c", "utils.c", "lib.c"],
    )
    assert program.sources == ["main.c", "utils.c", "lib.c"]


def test_environment_default() -> None:
    env = Environment()
    assert env.programs == []


def test_environment_getitem_setitem() -> None:
    env = Environment()
    env["CC"] = "gcc"
    assert env["CC"] == "gcc"


def test_environment_getitem_missing() -> None:
    env = Environment()
    assert env["NONEXISTENT"] is None


def test_environment_contains() -> None:
    env = Environment()
    env["CC"] = "gcc"
    assert "CC" in env
    assert "CXX" not in env


def test_environment_program_method() -> None:
    env = Environment()
    program = env.Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
    )
    assert isinstance(program, Program)
    assert program.name == "myapp"
    assert program in env.programs


def test_environment_multiple_programs() -> None:
    env = Environment()
    prog1 = env.Program(name="app1", languages=[Language.C], sources=["app1.c"])
    prog2 = env.Program(name="app2", languages=[Language.C], sources=["app2.c"])
    assert len(env.programs) == 2
    assert env.programs[0] is prog1
    assert env.programs[1] is prog2


def test_environment_vars_isolation() -> None:
    env1 = Environment()
    env2 = Environment()
    env1["CC"] = "gcc"
    env2["CC"] = "clang"
    assert env1["CC"] == "gcc"
    assert env2["CC"] == "clang"


def test_environment_programs_isolation() -> None:
    env1 = Environment()
    env2 = Environment()
    env1.Program(name="app1", languages=[Language.C], sources=["app1.c"])
    assert len(env1.programs) == 1
    assert len(env2.programs) == 0


def test_ensure_cc_already_set(mocker: MockerFixture) -> None:
    mock_debug = mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["CC"] = "/usr/bin/gcc"
    env.ensure_cc()
    mock_debug.assert_called_once_with("CC is set")
    assert env["CC"] == "/usr/bin/gcc"


def test_ensure_cc_linux_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "linux")
    mocker.patch("ezbuild.environment.which", return_value="/usr/bin/cc")
    mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env.ensure_cc()
    assert env["CC"] == "/usr/bin/cc"


def test_ensure_cc_linux_not_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "linux")
    mocker.patch("ezbuild.environment.which", return_value=None)
    mocker.patch("ezbuild.environment.debug")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    with pytest.raises(Exit):
        env.ensure_cc()
    mock_error.assert_called_once_with("cc not found")


def test_ensure_cc_unsupported_platform(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "win32")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    with pytest.raises(Exit):
        env.ensure_cc()
    mock_error.assert_called_once_with("Unsupported platform")


def test_ensure_ccld_already_set(mocker: MockerFixture) -> None:
    mock_debug = mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["CCLD"] = "/usr/bin/ld"
    env.ensure_ccld()
    mock_debug.assert_called_once_with("CCLD is set")
    assert env["CCLD"] == "/usr/bin/ld"


def test_ensure_ccld_not_set(mocker: MockerFixture) -> None:
    mock_debug = mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["CC"] = "/usr/bin/gcc"
    env.ensure_ccld()
    mock_debug.assert_called_once_with("CCLD is not set, using CC")
    assert env["CCLD"] == "/usr/bin/gcc"


def test_ensure_cxx_requires_cc(mocker: MockerFixture) -> None:
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    with pytest.raises(Exit):
        env.ensure_cxx()
    mock_error.assert_called_once_with("CXX requires CC")


def test_ensure_cxx_already_set(mocker: MockerFixture) -> None:
    mock_debug = mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["CC"] = "/usr/bin/gcc"
    env["CXX"] = "/usr/bin/g++"
    env.ensure_cxx()
    mock_debug.assert_called_once_with("CXX is set")
    assert env["CXX"] == "/usr/bin/g++"


def test_ensure_cxx_linux_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "linux")
    mocker.patch("ezbuild.environment.which", return_value="/usr/bin/c++")
    mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["CC"] = "/usr/bin/gcc"
    env.ensure_cxx()
    assert env["CXX"] == "/usr/bin/c++"


def test_ensure_cxx_linux_not_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "linux")
    mocker.patch("ezbuild.environment.which", return_value=None)
    mocker.patch("ezbuild.environment.debug")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    env["CC"] = "/usr/bin/gcc"
    with pytest.raises(Exit):
        env.ensure_cxx()
    mock_error.assert_called_once_with("c++ not found")


def test_ensure_cxx_unsupported_platform(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "win32")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    env["CC"] = "/usr/bin/gcc"
    with pytest.raises(Exit):
        env.ensure_cxx()
    mock_error.assert_called_once_with("Unsupported platform")


def test_ensure_cxxld_requires_ccld(mocker: MockerFixture) -> None:
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    with pytest.raises(Exit):
        env.ensure_cxxld()
    mock_error.assert_called_once_with("CXXLD requires CCLD")


def test_ensure_cxxld_already_set(mocker: MockerFixture) -> None:
    mock_debug = mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["CCLD"] = "/usr/bin/ld"
    env["CXXLD"] = "/usr/bin/ld"
    env.ensure_cxxld()
    mock_debug.assert_called_once_with("CXXLD is set")
    assert env["CXXLD"] == "/usr/bin/ld"


def test_ensure_cxxld_not_set(mocker: MockerFixture) -> None:
    mock_debug = mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["CCLD"] = "/usr/bin/gcc"
    env["CXX"] = "/usr/bin/g++"
    env.ensure_cxxld()
    mock_debug.assert_called_once_with("CXXLD is not set, using CXX")
    assert env["CXXLD"] == "/usr/bin/g++"
