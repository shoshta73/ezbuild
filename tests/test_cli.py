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
