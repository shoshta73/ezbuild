import os
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from ezbuild.commands.init import init

if TYPE_CHECKING:
    from pathlib import Path


def test_init_c_language(tmp_path: Path) -> None:
    """Test successful initialization with C language."""
    os.chdir(tmp_path)
    exit_code, message = init(language="c", name="myproject")

    assert exit_code == 0
    assert message == ""

    build_ezbuild = tmp_path / "build.ezbuild"
    assert build_ezbuild.exists()

    source_file = tmp_path / "myproject.c"
    assert source_file.exists()

    content = build_ezbuild.read_text()
    assert "env = Environment()" in content
    assert "name='myproject'" in content
    assert "Language.C" in content
    assert "sources=['myproject.c']" in content


def test_init_cxx_language(tmp_path: Path) -> None:
    """Test successful initialization with C++ language."""
    os.chdir(tmp_path)
    exit_code, message = init(language="cxx", name="myproject")

    assert exit_code == 0
    assert message == ""

    build_ezbuild = tmp_path / "build.ezbuild"
    assert build_ezbuild.exists()

    source_file = tmp_path / "myproject.cxx"
    assert source_file.exists()

    content = build_ezbuild.read_text()
    assert "Language.CXX" in content
    assert "sources=['myproject.cxx']" in content


@pytest.mark.parametrize("lang", ["cxx", "c++", "cc", "cpp"])
def test_init_cxx_variants(tmp_path: Path, lang: str) -> None:
    """Test different C++ language variants."""
    os.chdir(tmp_path)
    exit_code, message = init(language=lang, name="myproject")

    assert exit_code == 0
    assert message == ""

    build_ezbuild = tmp_path / "build.ezbuild"
    content = build_ezbuild.read_text()
    assert "Language.CXX" in content


def test_init_directory_not_empty(tmp_path: Path) -> None:
    """Test error when directory is not empty."""
    os.chdir(tmp_path)
    (tmp_path / "somefile.txt").touch()

    exit_code, message = init(language="c", name="myproject")

    assert exit_code == 1
    assert "not empty" in message.lower()


def test_init_unsupported_language(tmp_path: Path) -> None:
    """Test error for unsupported language."""
    os.chdir(tmp_path)
    exit_code, message = init(language="rust", name="myproject")

    assert exit_code == 2
    assert "Unsupported language" in message


@patch("ezbuild.commands.init.prompt")
def test_init_default_name_from_directory(mock_prompt, tmp_path: Path) -> None:
    """Test using directory name as default project name."""
    os.chdir(tmp_path)
    mock_prompt.return_value = tmp_path.name
    exit_code, message = init(language="c", name=None)

    assert exit_code == 0
    assert message == ""

    build_ezbuild = tmp_path / "build.ezbuild"
    content = build_ezbuild.read_text()
    assert f"name='{tmp_path.name}'" in content


def test_init_c_source_content(tmp_path: Path) -> None:
    """Test that C source file has correct content."""
    os.chdir(tmp_path)
    init(language="c", name="myproject")

    source_file = tmp_path / "myproject.c"
    content = source_file.read_text()
    assert "#include <stdio.h>" in content
    assert 'printf("Hello, World!\\n");' in content
    assert "return 0;" in content


def test_init_cxx_source_content(tmp_path: Path) -> None:
    """Test that C++ source file has correct content."""
    os.chdir(tmp_path)
    init(language="cxx", name="myproject")

    source_file = tmp_path / "myproject.cxx"
    content = source_file.read_text()
    assert "#include <iostream>" in content
    assert 'std::cout << "Hello, World!\\n";' in content
    assert "return 0;" in content


@patch("ezbuild.commands.init.prompt")
def test_init_interactive_language(mock_prompt, tmp_path: Path) -> None:
    """Test interactive language selection."""
    from ezbuild import Language

    os.chdir(tmp_path)
    mock_prompt.side_effect = [tmp_path.name, Language.C]
    exit_code, message = init(language=None, name=None)

    assert exit_code == 0
    assert message == ""
    assert mock_prompt.call_count == 2
