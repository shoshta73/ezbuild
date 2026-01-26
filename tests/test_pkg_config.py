from typing import TYPE_CHECKING

import pytest
from typer import Exit

from ezbuild.environment import Environment, Program, SharedLibrary, StaticLibrary
from ezbuild.language import Language

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_system_library_creation() -> None:
    from ezbuild.environment import SystemLibrary

    lib = SystemLibrary(
        name="libcurl",
        compile_flags=["-I/usr/include/curl"],
        link_flags=["-lcurl"],
    )
    assert lib.name == "libcurl"
    assert lib.compile_flags == ["-I/usr/include/curl"]
    assert lib.link_flags == ["-lcurl"]


def test_system_library_empty_flags() -> None:
    from ezbuild.environment import SystemLibrary

    lib = SystemLibrary(name="testlib")
    assert lib.name == "testlib"
    assert lib.compile_flags == []
    assert lib.link_flags == []


def test_program_with_system_dependencies() -> None:
    program = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        system_dependencies=["libcurl"],
    )
    assert program.system_dependencies == ["libcurl"]


def test_program_multiple_system_dependencies() -> None:
    program = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        system_dependencies=["libcurl", "openssl"],
    )
    assert program.system_dependencies == ["libcurl", "openssl"]


def test_program_default_system_dependencies() -> None:
    program = Program(name="myapp", languages=[Language.C], sources=["main.c"])
    assert program.system_dependencies == []


def test_static_library_with_system_dependencies() -> None:
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        system_dependencies=["libcurl"],
    )
    assert lib.system_dependencies == ["libcurl"]


def test_shared_library_with_system_dependencies() -> None:
    lib = SharedLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        system_dependencies=["libcurl"],
    )
    assert lib.system_dependencies == ["libcurl"]


def test_environment_program_with_system_dependencies() -> None:
    env = Environment()
    program = env.Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        system_dependencies=["libcurl"],
    )
    assert isinstance(program, Program)
    assert program.system_dependencies == ["libcurl"]
    assert program in env.programs


def test_environment_static_library_with_system_dependencies() -> None:
    env = Environment()
    lib = env.StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        system_dependencies=["libcurl"],
    )
    assert isinstance(lib, StaticLibrary)
    assert lib.system_dependencies == ["libcurl"]
    assert lib in env.static_libraries


def test_environment_shared_library_with_system_dependencies() -> None:
    env = Environment()
    lib = env.SharedLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        system_dependencies=["libcurl"],
    )
    assert isinstance(lib, SharedLibrary)
    assert lib.system_dependencies == ["libcurl"]
    assert lib in env.shared_libraries


def test_ensure_pkg_config_unix_available(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.pkg_config.platform", "linux")
    mocker.patch("ezbuild.pkg_config.which", return_value="/usr/bin/pkg-config")
    mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env.ensure_pkg_config()


def test_ensure_pkg_config_unix_not_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "linux")
    mocker.patch("ezbuild.environment.which", return_value=None)
    mocker.patch("ezbuild.environment.debug")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    with pytest.raises(Exit):
        env.ensure_pkg_config()
    mock_error.assert_called_once_with("pkg-config not found")


def test_ensure_pkg_config_windows(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "win32")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    with pytest.raises(Exit):
        env.ensure_pkg_config()
    mock_error.assert_called_once_with("pkg-config is only supported on Unix systems")


def test_pkg_config_is_available_unix(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.pkg_config.platform", "linux")
    mocker.patch("ezbuild.pkg_config.which", return_value="/usr/bin/pkg-config")
    from ezbuild import pkg_config

    assert pkg_config.is_available()


def test_pkg_config_is_available_not_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.pkg_config.platform", "linux")
    mocker.patch("ezbuild.pkg_config.which", return_value=None)
    from ezbuild import pkg_config

    assert not pkg_config.is_available()


def test_pkg_config_is_available_windows(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.pkg_config.platform", "win32")
    from ezbuild import pkg_config

    assert not pkg_config.is_available()


def test_pkg_config_query_package_success(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.pkg_config.platform", "linux")
    mocker.patch("ezbuild.pkg_config.which", return_value="/usr/bin/pkg-config")
    mocker.patch("ezbuild.pkg_config.debug")

    cflags_mock = mocker.Mock()
    cflags_mock.stdout.decode.return_value = "-I/usr/include/curl -DCURL_FOUND"
    cflags_mock.stderr.decode.return_value = ""
    cflags_mock.returncode = 0

    libs_mock = mocker.Mock()
    libs_mock.stdout.decode.return_value = "-lcurl -lssl"
    libs_mock.stderr.decode.return_value = ""
    libs_mock.returncode = 0

    mocker.patch(
        "ezbuild.pkg_config.subprocess.run", side_effect=[cflags_mock, libs_mock]
    )

    from ezbuild import pkg_config

    lib = pkg_config.query_package("libcurl")
    assert lib.name == "libcurl"
    assert lib.compile_flags == ["-I/usr/include/curl", "-DCURL_FOUND"]
    assert lib.link_flags == ["-lcurl", "-lssl"]


def test_pkg_config_query_package_not_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.pkg_config.platform", "linux")
    mocker.patch("ezbuild.pkg_config.which", return_value="/usr/bin/pkg-config")

    import subprocess

    mocker.patch(
        "ezbuild.pkg_config.subprocess.run",
        side_effect=subprocess.CalledProcessError(
            1, "pkg-config", stderr=b"Package 'nonexistent' was not found"
        ),
    )

    from ezbuild import pkg_config

    with pytest.raises(RuntimeError) as exc_info:
        pkg_config.query_package("nonexistent")
    assert "not found" in str(exc_info.value).lower()


def test_pkg_config_query_package_unavailable(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.pkg_config.platform", "linux")
    mocker.patch("ezbuild.pkg_config.which", return_value=None)

    from ezbuild import pkg_config

    with pytest.raises(RuntimeError) as exc_info:
        pkg_config.query_package("libcurl")
    assert "not available" in str(exc_info.value).lower()


def test_pkg_config_query_multiple_packages(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.pkg_config.platform", "linux")
    mocker.patch("ezbuild.pkg_config.which", return_value="/usr/bin/pkg-config")
    mocker.patch("ezbuild.pkg_config.debug")

    cflags_mock = mocker.Mock()
    cflags_mock.stdout.decode.return_value = "-I/usr/include/curl"
    cflags_mock.stderr.decode.return_value = ""
    cflags_mock.returncode = 0

    libs_mock = mocker.Mock()
    libs_mock.stdout.decode.return_value = "-lcurl"
    libs_mock.stderr.decode.return_value = ""
    libs_mock.returncode = 0

    mocker.patch(
        "ezbuild.pkg_config.subprocess.run",
        side_effect=[cflags_mock, libs_mock, cflags_mock, libs_mock],
    )

    from ezbuild import pkg_config

    libs = pkg_config.query_multiple_packages(["libcurl", "libcurl"])
    assert len(libs) == 1
    assert "libcurl" in libs
    assert libs["libcurl"].name == "libcurl"
