from importlib.metadata import version

import pytest
from typer.testing import CliRunner

from ezbuild.__main__ import cli

runner = CliRunner()


@pytest.mark.parametrize("flag", ["-V", "--version"])
def test_version(flag: str) -> None:
    result = runner.invoke(cli, [flag])
    assert result.exit_code == 0
    assert result.output.strip() == f"ezbuild {version('ezbuild')}"


def test_init_c_language(tmp_path) -> None:
    """Test init command with C language."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "myproject", "--language", "c"])
        assert result.exit_code == 0

        from pathlib import Path

        cwd = Path.cwd()
        assert (cwd / "build.ezbuild").exists()
        assert (cwd / "myproject.c").exists()


def test_init_cxx_language(tmp_path) -> None:
    """Test init command with C++ language."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "myproject", "--language", "cxx"])
        assert result.exit_code == 0

        from pathlib import Path

        cwd = Path.cwd()
        assert (cwd / "build.ezbuild").exists()
        assert (cwd / "myproject.cxx").exists()


def test_init_language_short_flag(tmp_path) -> None:
    """Test init command with short language flag."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "myproject", "-l", "c"])
        assert result.exit_code == 0

        from pathlib import Path

        cwd = Path.cwd()
        assert (cwd / "build.ezbuild").exists()
        assert (cwd / "myproject.c").exists()


@pytest.mark.parametrize("lang", ["cxx", "c++", "cc", "cpp"])
def test_init_cxx_variants(tmp_path, lang: str) -> None:
    """Test init command with different C++ language variants."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "myproject", "--language", lang])
        assert result.exit_code == 0

        from pathlib import Path

        cwd = Path.cwd()
        assert (cwd / "build.ezbuild").exists()
        assert (cwd / "myproject.cxx").exists()


def test_init_non_empty_directory(tmp_path) -> None:
    """Test init command fails in non-empty directory."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        from pathlib import Path

        (Path.cwd() / "existing.txt").touch()
        result = runner.invoke(cli, ["init", "myproject", "--language", "c"])
        assert result.exit_code == 1
        assert "not empty" in result.output.lower()


def test_init_unsupported_language(tmp_path) -> None:
    """Test init command fails with unsupported language."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "myproject", "--language", "rust"])
        assert result.exit_code == 2
        assert "Unsupported language" in result.output


def test_clean_removes_build_dir(tmp_path) -> None:
    """Test clean command removes build directory."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        from pathlib import Path

        build_dir = Path.cwd() / "build"
        build_dir.mkdir()
        (build_dir / "somefile.txt").write_text("test")

        result = runner.invoke(cli, ["clean"])
        assert result.exit_code == 0
        assert not build_dir.exists()


def test_clean_nothing_to_clean(tmp_path) -> None:
    """Test clean command when build directory doesn't exist."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        from pathlib import Path

        build_dir = Path.cwd() / "build"

        result = runner.invoke(cli, ["clean"])
        assert result.exit_code == 0
        assert not build_dir.exists()


def test_clean_removes_nested_files(tmp_path) -> None:
    """Test clean command removes nested files and directories."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        from pathlib import Path

        build_dir = Path.cwd() / "build"
        bin_dir = build_dir / "bin"
        lib_dir = build_dir / "lib"
        bin_dir.mkdir(parents=True)
        lib_dir.mkdir(parents=True)
        (bin_dir / "executable").write_text("binary")
        (lib_dir / "library.a").write_text("archive")
        (build_dir / "compile_commands.json").write_text("{}")

        result = runner.invoke(cli, ["clean"])
        assert result.exit_code == 0
        assert not build_dir.exists()
