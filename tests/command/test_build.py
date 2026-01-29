import os
from typing import TYPE_CHECKING

from ezbuild import Language, Program, SharedLibrary, StaticLibrary
from ezbuild.commands.build import _collect_public_defines, _format_define, build

if TYPE_CHECKING:
    from pathlib import Path


def test_format_define_simple() -> None:
    """Test formatting a simple define without spaces."""
    result = _format_define("VERSION=1.0")
    assert result == "-DVERSION=1.0"


def test_format_define_with_spaces() -> None:
    """Test formatting a define with spaces (should be quoted)."""
    result = _format_define('MESSAGE="Hello World"')
    assert result == '"-DMESSAGE="Hello World""'


def test_format_define_no_value() -> None:
    """Test formatting a define without a value."""
    result = _format_define("DEBUG")
    assert result == "-DDEBUG"


def test_collect_public_defines_no_dependencies() -> None:
    """Test collecting public defines when there are no dependencies."""
    target = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "myapp": target,
    }
    public_defines = _collect_public_defines(target, targets)
    assert public_defines == []


def test_collect_public_defines_single_dependency() -> None:
    """Test collecting public defines from a single dependency."""
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        public_defines=["LIB_VERSION=1.0"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "mylib": lib,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert public_defines == ["LIB_VERSION=1.0"]


def test_collect_public_defines_multiple_dependencies() -> None:
    """Test collecting public defines from multiple dependencies."""
    lib1 = StaticLibrary(
        name="lib1",
        languages=[Language.C],
        sources=["lib1.c"],
        public_defines=["LIB1_VERSION=1.0"],
    )
    lib2 = StaticLibrary(
        name="lib2",
        languages=[Language.C],
        sources=["lib2.c"],
        public_defines=["LIB2_VERSION=2.0"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["lib1", "lib2"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "lib1": lib1,
        "lib2": lib2,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert sorted(public_defines) == ["LIB1_VERSION=1.0", "LIB2_VERSION=2.0"]


def test_collect_public_defines_transitive_dependencies() -> None:
    """Test collecting public defines from transitive dependencies."""
    lib1 = StaticLibrary(
        name="lib1",
        languages=[Language.C],
        sources=["lib1.c"],
        public_defines=["LIB1_VERSION=1.0"],
    )
    lib2 = StaticLibrary(
        name="lib2",
        languages=[Language.C],
        sources=["lib2.c"],
        dependencies=["lib1"],
        public_defines=["LIB2_VERSION=2.0"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["lib2"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "lib1": lib1,
        "lib2": lib2,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert sorted(public_defines) == ["LIB1_VERSION=1.0", "LIB2_VERSION=2.0"]


def test_collect_public_defines_mixed_types() -> None:
    """Test collecting public defines from mixed library types."""
    lib1 = StaticLibrary(
        name="lib1",
        languages=[Language.C],
        sources=["lib1.c"],
        public_defines=["STATIC_DEFINE=1"],
    )
    lib2 = SharedLibrary(
        name="lib2",
        languages=[Language.C],
        sources=["lib2.c"],
        public_defines=["SHARED_DEFINE=2"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["lib1", "lib2"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "lib1": lib1,
        "lib2": lib2,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert sorted(public_defines) == ["SHARED_DEFINE=2", "STATIC_DEFINE=1"]


def test_collect_public_defines_no_public_defines() -> None:
    """Test collecting public defines when none exist."""
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "mylib": lib,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert public_defines == []


def test_collect_public_defines_private_defines_not_collected() -> None:
    """Test that private defines are not collected."""
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        defines=["PRIVATE_DEFINE=1"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "mylib": lib,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert public_defines == []


def test_collect_public_defines_both_public_and_private() -> None:
    """Test collecting only public defines when both exist."""
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        defines=["PRIVATE_DEFINE=1"],
        public_defines=["PUBLIC_DEFINE=2"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "mylib": lib,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert public_defines == ["PUBLIC_DEFINE=2"]


def test_build_no_build_file(tmp_path: Path) -> None:
    """Test build when build.ezbuild does not exist."""
    os.chdir(tmp_path)
    exit_code, message = build()
    assert exit_code == 1
    assert message == "build.ezbuild does not exist"


def test_build_simple_program(tmp_path: Path) -> None:
    """Test building a simple C program."""
    os.chdir(tmp_path)

    build_file_content = """
env = Environment()
myapp = Program(
    name="myapp",
    languages=[Language.C],
    sources=["main.c"]
)
"""
    (tmp_path / "build.ezbuild").write_text(build_file_content)
    (tmp_path / "main.c").write_text(
        """
#include <stdio.h>
int main() {
    printf("Hello, World!\\n");
    return 0;
}
"""
    )

    exit_code, message = build()
    assert exit_code == 0
    assert message == ""
    assert (tmp_path / "build" / "bin" / "myapp").exists()


def test_build_simple_cxx_program(tmp_path: Path) -> None:
    """Test building a simple C++ program."""
    os.chdir(tmp_path)

    build_file_content = """
env = Environment()
myapp = Program(
    name="myapp",
    languages=[Language.CXX],
    sources=["main.cxx"]
)
"""
    (tmp_path / "build.ezbuild").write_text(build_file_content)
    (tmp_path / "main.cxx").write_text(
        """
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""
    )

    exit_code, message = build()
    assert exit_code == 0
    assert message == ""
    assert (tmp_path / "build" / "bin" / "myapp").exists()


def test_build_static_library(tmp_path: Path) -> None:
    """Test building a static library."""
    os.chdir(tmp_path)

    build_file_content = """
env = Environment()
mylib = StaticLibrary(
    name="mylib",
    languages=[Language.C],
    sources=["lib.c"]
)
"""
    (tmp_path / "build.ezbuild").write_text(build_file_content)
    (tmp_path / "lib.c").write_text(
        """
int add(int a, int b) {
    return a + b;
}
"""
    )

    exit_code, message = build()
    assert exit_code == 0
    assert message == ""
    assert (tmp_path / "build" / "lib" / "mylib.a").exists()


def test_build_shared_library(tmp_path: Path) -> None:
    """Test building a shared library."""
    os.chdir(tmp_path)

    build_file_content = """
env = Environment()
mylib = SharedLibrary(
    name="mylib",
    languages=[Language.C],
    sources=["lib.c"]
)
"""
    (tmp_path / "build.ezbuild").write_text(build_file_content)
    (tmp_path / "lib.c").write_text(
        """
int add(int a, int b) {
    return a + b;
}
"""
    )

    exit_code, message = build()
    assert exit_code == 0
    assert message == ""
    assert (tmp_path / "build" / "lib" / "mylib.so").exists()


def test_build_no_environment(tmp_path: Path) -> None:
    """Test build when no environment is defined."""
    os.chdir(tmp_path)

    build_file_content = """
Program(
    name="myapp",
    languages=[Language.C],
    sources=["main.c"]
)
"""
    (tmp_path / "build.ezbuild").write_text(build_file_content)

    exit_code, message = build()
    assert exit_code == 3
    assert message == "No build environment found"


def test_build_no_targets(tmp_path: Path) -> None:
    """Test build when no targets are defined."""
    os.chdir(tmp_path)

    build_file_content = "env = Environment()"
    (tmp_path / "build.ezbuild").write_text(build_file_content)

    exit_code, message = build()
    assert exit_code == 4
    assert message == "No targets found"


def test_build_creates_compile_commands_json(tmp_path: Path) -> None:
    """Test that build creates compile_commands.json."""
    os.chdir(tmp_path)

    build_file_content = """
env = Environment()
myapp = Program(
    name="myapp",
    languages=[Language.C],
    sources=["main.c"]
)
"""
    (tmp_path / "build.ezbuild").write_text(build_file_content)
    (tmp_path / "main.c").write_text("int main() { return 0; }")

    exit_code, _message = build()
    assert exit_code == 0
    assert (tmp_path / "build" / "compile_commands.json").exists()

    import json

    with (tmp_path / "build" / "compile_commands.json").open("r") as f:
        compile_commands = json.load(f)
    assert len(compile_commands) > 0
