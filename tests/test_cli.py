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
