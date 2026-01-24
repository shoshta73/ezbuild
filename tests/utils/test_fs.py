from typing import TYPE_CHECKING

from ezbuild.utils.fs import create_dir_if_not_exists

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


def test_create_dir_if_not_exists_creates_directory(tmp_path: Path) -> None:
    new_dir = tmp_path / "new_directory"
    create_dir_if_not_exists(new_dir)
    assert new_dir.exists()
    assert new_dir.is_dir()


def test_create_dir_if_not_exists_no_error_if_exists(tmp_path: Path) -> None:
    existing_dir = tmp_path / "existing"
    existing_dir.mkdir()
    create_dir_if_not_exists(existing_dir)
    assert existing_dir.exists()


def test_create_dir_if_not_exists_logs_debug(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    mock_debug = mocker.patch("ezbuild.utils.fs.debug")
    new_dir = tmp_path / "new_directory"
    create_dir_if_not_exists(new_dir)
    assert mock_debug.call_count == 2


def test_create_dir_if_not_exists_no_info_if_exists(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    mock_info = mocker.patch("ezbuild.utils.fs.info")
    existing_dir = tmp_path / "existing"
    existing_dir.mkdir()
    create_dir_if_not_exists(existing_dir)
    mock_info.assert_not_called()


def test_create_dir_if_not_exists_logs_info_when_created(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    mock_info = mocker.patch("ezbuild.utils.fs.info")
    new_dir = tmp_path / "new_directory"
    create_dir_if_not_exists(new_dir)
    mock_info.assert_called_once()
