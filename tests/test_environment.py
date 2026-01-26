from typing import TYPE_CHECKING

import pytest
from typer import Exit

from ezbuild.environment import Environment, Program, SharedLibrary, StaticLibrary
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


def test_static_library_creation() -> None:
    lib = StaticLibrary(name="mylib", languages=[Language.C], sources=["lib.c"])
    assert lib.name == "mylib"
    assert lib.languages == [Language.C]
    assert lib.sources == ["lib.c"]
    assert lib.dependencies == []


def test_static_library_with_dependencies() -> None:
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        dependencies=["dep1", "dep2"],
    )
    assert lib.dependencies == ["dep1", "dep2"]


def test_shared_library_creation() -> None:
    lib = SharedLibrary(name="mylib", languages=[Language.C], sources=["lib.c"])
    assert lib.name == "mylib"
    assert lib.languages == [Language.C]
    assert lib.sources == ["lib.c"]
    assert lib.dependencies == []


def test_shared_library_with_dependencies() -> None:
    lib = SharedLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        dependencies=["dep1", "dep2"],
    )
    assert lib.dependencies == ["dep1", "dep2"]


def test_program_with_dependencies() -> None:
    program = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["libfoo", "libbar"],
    )
    assert program.dependencies == ["libfoo", "libbar"]


def test_program_default_dependencies() -> None:
    program = Program(name="myapp", languages=[Language.C], sources=["main.c"])
    assert program.dependencies == []


def test_environment_static_library_method() -> None:
    env = Environment()
    lib = env.StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
    )
    assert isinstance(lib, StaticLibrary)
    assert lib.name == "mylib"
    assert lib in env.static_libraries


def test_environment_static_library_with_dependencies() -> None:
    env = Environment()
    lib = env.StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        dependencies=["dep1"],
    )
    assert lib.dependencies == ["dep1"]


def test_environment_multiple_static_libraries() -> None:
    env = Environment()
    lib1 = env.StaticLibrary(name="lib1", languages=[Language.C], sources=["lib1.c"])
    lib2 = env.StaticLibrary(name="lib2", languages=[Language.C], sources=["lib2.c"])
    assert len(env.static_libraries) == 2
    assert env.static_libraries[0] is lib1
    assert env.static_libraries[1] is lib2


def test_environment_shared_library_method() -> None:
    env = Environment()
    lib = env.SharedLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
    )
    assert isinstance(lib, SharedLibrary)
    assert lib.name == "mylib"
    assert lib in env.shared_libraries


def test_environment_shared_library_with_dependencies() -> None:
    env = Environment()
    lib = env.SharedLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        dependencies=["dep1"],
    )
    assert lib.dependencies == ["dep1"]


def test_environment_multiple_shared_libraries() -> None:
    env = Environment()
    lib1 = env.SharedLibrary(name="lib1", languages=[Language.C], sources=["lib1.c"])
    lib2 = env.SharedLibrary(name="lib2", languages=[Language.C], sources=["lib2.c"])
    assert len(env.shared_libraries) == 2
    assert env.shared_libraries[0] is lib1
    assert env.shared_libraries[1] is lib2


def test_environment_static_libraries_isolation() -> None:
    env1 = Environment()
    env2 = Environment()
    env1.StaticLibrary(name="lib1", languages=[Language.C], sources=["lib1.c"])
    assert len(env1.static_libraries) == 1
    assert len(env2.static_libraries) == 0


def test_environment_shared_libraries_isolation() -> None:
    env1 = Environment()
    env2 = Environment()
    env1.SharedLibrary(name="lib1", languages=[Language.C], sources=["lib1.c"])
    assert len(env1.shared_libraries) == 1
    assert len(env2.shared_libraries) == 0


def test_ensure_ar_already_set(mocker: MockerFixture) -> None:
    mock_debug = mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["AR"] = "/usr/bin/ar"
    env.ensure_ar()
    mock_debug.assert_called_once_with("AR is set")
    assert env["AR"] == "/usr/bin/ar"


def test_ensure_ar_linux_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "linux")
    mocker.patch("ezbuild.environment.which", return_value="/usr/bin/ar")
    mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env.ensure_ar()
    assert env["AR"] == "/usr/bin/ar"


def test_ensure_ar_linux_not_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "linux")
    mocker.patch("ezbuild.environment.which", return_value=None)
    mocker.patch("ezbuild.environment.debug")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    with pytest.raises(Exit):
        env.ensure_ar()
    mock_error.assert_called_once_with("ar not found")


def test_ensure_ar_unsupported_platform(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "win32")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    with pytest.raises(Exit):
        env.ensure_ar()
    mock_error.assert_called_once_with("Unsupported platform")


def test_ensure_ranlib_requires_ar(mocker: MockerFixture) -> None:
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    with pytest.raises(Exit):
        env.ensure_ranlib()
    mock_error.assert_called_once_with("AR requires AR")


def test_ensure_ranlib_already_set(mocker: MockerFixture) -> None:
    mock_debug = mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["AR"] = "/usr/bin/ar"
    env["RANLIB"] = "/usr/bin/ranlib"
    env.ensure_ranlib()
    mock_debug.assert_called_once_with("RANLIB is set")
    assert env["RANLIB"] == "/usr/bin/ranlib"


def test_ensure_ranlib_linux_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "linux")
    mocker.patch("ezbuild.environment.which", return_value="/usr/bin/ranlib")
    mocker.patch("ezbuild.environment.debug")
    env = Environment()
    env["AR"] = "/usr/bin/ar"
    env.ensure_ranlib()
    assert env["RANLIB"] == "/usr/bin/ranlib"


def test_ensure_ranlib_linux_not_found(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "linux")
    mocker.patch("ezbuild.environment.which", return_value=None)
    mocker.patch("ezbuild.environment.debug")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    env["AR"] = "/usr/bin/ar"
    with pytest.raises(Exit):
        env.ensure_ranlib()
    mock_error.assert_called_once_with("ranlib not found")


def test_ensure_ranlib_unsupported_platform(mocker: MockerFixture) -> None:
    mocker.patch("ezbuild.environment.platform", "win32")
    mock_error = mocker.patch("ezbuild.environment.error")
    env = Environment()
    env["AR"] = "/usr/bin/ar"
    with pytest.raises(Exit):
        env.ensure_ranlib()
    mock_error.assert_called_once_with("Unsupported platform")
