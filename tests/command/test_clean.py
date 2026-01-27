import os

from ezbuild.commands.clean import clean


def test_clean_removes_build_dir(tmp_path) -> None:
    """Test clean removes the build directory."""
    os.chdir(tmp_path)
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "somefile.txt").write_text("test")

    assert build_dir.exists()
    clean()
    assert not build_dir.exists()


def test_clean_nothing_to_clean(tmp_path) -> None:
    """Test clean when build directory doesn't exist."""
    os.chdir(tmp_path)
    build_dir = tmp_path / "build"

    assert not build_dir.exists()
    clean()
    assert not build_dir.exists()


def test_clean_removes_nested_files(tmp_path) -> None:
    """Test clean removes nested files and directories."""
    os.chdir(tmp_path)
    build_dir = tmp_path / "build"
    bin_dir = build_dir / "bin"
    lib_dir = build_dir / "lib"
    int_dir = build_dir / "myproject"
    bin_dir.mkdir(parents=True)
    lib_dir.mkdir(parents=True)
    int_dir.mkdir(parents=True)
    (bin_dir / "executable").write_text("binary")
    (lib_dir / "library.a").write_text("archive")
    (int_dir / "source.o").write_text("object")
    (build_dir / "compile_commands.json").write_text("{}")

    assert build_dir.exists()
    clean()
    assert not build_dir.exists()


def test_clean_empty_build_dir(tmp_path) -> None:
    """Test clean removes empty build directory."""
    os.chdir(tmp_path)
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    assert build_dir.exists()
    clean()
    assert not build_dir.exists()


def test_clean_does_not_remove_other_dirs(tmp_path) -> None:
    """Test clean only removes build directory."""
    os.chdir(tmp_path)
    build_dir = tmp_path / "build"
    src_dir = tmp_path / "src"
    build_dir.mkdir()
    src_dir.mkdir()
    (src_dir / "main.c").write_text("int main() { return 0; }")

    clean()
    assert not build_dir.exists()
    assert src_dir.exists()
    assert (src_dir / "main.c").exists()
