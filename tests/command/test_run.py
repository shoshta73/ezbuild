import os
from typing import TYPE_CHECKING

from ezbuild.commands.run import run

if TYPE_CHECKING:
    from pathlib import Path


def test_run_missing_binary(tmp_path: Path) -> None:
    """Test run when binary doesn't exist and build fails."""
    os.chdir(tmp_path)

    build_file_content = """
env = Environment()
"""
    (tmp_path / "build.ezbuild").write_text(build_file_content)

    exit_code, message = run(name="myapp")
    assert exit_code == 1
    assert "Failed to build project myapp" in message


def test_run_existing_binary_success(tmp_path: Path) -> None:
    """Test run when binary exists and runs successfully."""
    os.chdir(tmp_path)

    bin_dir = tmp_path / "build" / "bin"
    bin_dir.mkdir(parents=True)

    executable_path = bin_dir / "myapp"
    executable_path.write_text("#!/bin/sh\necho 'Hello, World!'")
    executable_path.chmod(0o755)

    exit_code, message = run(name="myapp")
    assert exit_code == 0
    assert message == ""


def test_run_existing_binary_failure(tmp_path: Path) -> None:
    """Test run when binary exists but fails."""
    os.chdir(tmp_path)

    bin_dir = tmp_path / "build" / "bin"
    bin_dir.mkdir(parents=True)

    executable_path = bin_dir / "myapp"
    executable_path.write_text("#!/bin/sh\nexit 1")
    executable_path.chmod(0o755)

    exit_code, message = run(name="myapp")
    assert exit_code == 2
    assert "Failed to run" in message


def test_run_builds_then_runs(tmp_path: Path) -> None:
    """Test run builds the project first if binary doesn't exist."""
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

    exit_code, message = run(name="myapp")
    assert exit_code == 0
    assert message == ""
    assert (tmp_path / "build" / "bin" / "myapp").exists()


def test_run_builds_cxx_program(tmp_path: Path) -> None:
    """Test run builds and runs a C++ program."""
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

    exit_code, message = run(name="myapp")
    assert exit_code == 0
    assert message == ""
    assert (tmp_path / "build" / "bin" / "myapp").exists()


def test_run_no_build_file(tmp_path: Path) -> None:
    """Test run when build.ezbuild doesn't exist."""
    os.chdir(tmp_path)

    exit_code, message = run(name="myapp")
    assert exit_code == 1
    assert "Failed to build project myapp" in message


def test_run_nonexistent_target_name(tmp_path: Path) -> None:
    """Test run with a non-existent target name."""
    os.chdir(tmp_path)

    build_file_content = """
env = Environment()
otherapp = Program(
    name="otherapp",
    languages=[Language.C],
    sources=["other.c"]
)
"""
    (tmp_path / "build.ezbuild").write_text(build_file_content)

    exit_code, message = run(name="myapp")
    assert exit_code == 1
    assert "Failed to build project myapp" in message


def test_run_binary_in_nonexistent_build_dir(tmp_path: Path) -> None:
    """Test run when binary is supposed to be in non-existent build directory."""
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

    exit_code, message = run(name="myapp")
    assert exit_code == 0
    assert message == ""
