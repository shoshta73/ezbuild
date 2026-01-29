# Agent Guidelines for Ezbuild Repository

## Build, Test, and Lint Commands

### Essential Commands
- **Run all tests**: `pytest`
- **Run a single test**: `pytest tests/test_cli.py::test_version`
- **Run tests with coverage**: `pytest --cov=ezbuild`
- **Lint code**: `ruff check src/ tests/`
- **Format code**: `ruff format src/ tests/`
- **Lint and format**: `ruff check --fix src/ tests/ && ruff format src/ tests/`
- **Build package**: `uv build`
- **Install dependencies**: `uv sync`

### Project Structure
- Source code: `src/ezbuild/`
- Tests: `tests/`
- Examples: `examples/`
- Main entry point: `src/ezbuild/__main__.py`

## Code Style Guidelines

### Imports
- Order: standard library → third-party → local imports
- Separate each import group with a blank line
- Use `from typing import Annotated` for type annotations
- Import specific classes/functions: `from ezbuild import CompileCommand, Environment`
- Example:
  ```python
  import json
  import shutil
  from pathlib import Path
  from typing import Annotated

  import typer

  from ezbuild import CompileCommand, Environment
  ```

### Formatting
- 4-space indentation for Python files
- Double quotes for strings
- Max line length: 88 characters
- LF line endings
- Trailing newline required
- No trailing whitespace

### Types
- Use modern type hints with `list[T]` syntax, not `List[T]`
- Optional types with `| None` syntax: `str | None`
- Type annotations required on all function signatures
- Use `Annotated` for adding metadata to parameters
- Use `TYPE_CHECKING` for type-only imports to avoid circular dependencies:
  ```python
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from pathlib import Path
  ```
- Example:
  ```python
  def build(name: Annotated[str | None, typer.Argument()] = None) -> None:
  ```

### Naming Conventions
- Modules: lowercase with underscores (`compile_command.py`)
- Classes: PascalCase (`CompileCommand`, `Environment`)
- Functions/variables: snake_case (`build_project`, `compile_commands`)
- Constants: UPPERCASE (`MAX_LINE_LENGTH`)
- Type variables: PascalCase

### Error Handling
- Use `typer.Exit` for CLI exit (not `sys.exit`)
- Log errors with `log.error()`, info with `log.info()`, debug with `log.debug()`
- Check subprocess return codes: `if result.returncode != 0:`
- Provide descriptive error messages
- Raise `typer.Exit` on critical failures
- Example:
  ```python
  if not (cwd / "build.ezbuild").exists():
      log.error("build.ezbuild does not exist")
      raise typer.Exit
  ```

### Code Patterns
- Use `pathlib.Path` for file operations, not `os.path`
- Use `Path.open(cwd / "build.ezbuild", "w")` instead of `open()` for file I/O
- Use `dataclass` with `field(default_factory=list)` for mutable defaults
- Use `Enum` for constants (with `auto()` for auto-numbered values)
- Use `@property` decorators for computed attributes and dict wrappers
- Inherit from `dict[str, str]` with property-based access for JSON-serializable types
- Expose public API via `__all__` in `__init__.py`
- Use `typer.echo()` for CLI output, not `print()`
- Use `shutil.which()` to check command availability
- Platform detection: `from sys import platform`

### CLI Development
- Use `typer` for CLI commands
- Use `Annotated` for argument/option metadata
- Provide docstrings for commands
- Use `@cli.command()` for subcommands
- Use `@cli.callback()` for main entry point
- Version flag should be eager and use callback

### Testing
- Use `pytest` with parametrize for multiple test cases
- Use `CliRunner` for CLI testing
- Use `pytest-mock` with `mocker.patch()` for mocking
- Use `pytest.raises()` for exception testing
- Use `tmp_path` fixture for temporary directories
- Use `runner.isolated_filesystem(temp_dir=tmp_path)` for test isolation
- Assert exit codes and output
- Test structure:
  ```python
  @pytest.mark.parametrize("flag", ["-V", "--version"])
  def test_version(flag: str) -> None:
      result = runner.invoke(cli, [flag])
      assert result.exit_code == 0
  ```

### String Formatting
- Use f-strings for string formatting: `f"Building {program.name}"`
- Escape newlines in multi-line strings: `f"Hello, World!\n"`
- Double quotes for all strings (not single quotes)

### Dataclasses
- Use `@dataclass` decorator
- Use `field(default_factory=list/dict)` for mutable defaults
- Type all fields explicitly
- Example:
  ```python
  @dataclass
  class Environment:
      programs: list[Program] = field(default_factory=list)
      _vars: dict[str, object] = field(default_factory=dict)
  ```

### Subprocess Usage
- Use `subprocess.run()` for command execution
- For build commands (compilation/linking): split command into list, no `shell=True`
- For running executables: use string path without capture_output
- Always capture output with `capture_output=True` for build commands
- Check return codes and log stderr on failure
- Example:
  ```python
  cmd_list = build_env["CC"].split()
  result = subprocess.run(cmd_list, capture_output=True)
  if result.returncode != 0:
      log.error("Command failed")
      log.debug(f"Error: {result.stderr.decode()}")
  ```

## Tools Configuration
- **Ruff**: Linting and formatting (configured in `pyproject.toml`)
- **Pytest**: Test runner (configured in `pyproject.toml`)
- **Python**: 3.14+ (see `.python-version`)
- **EditorConfig**: Consistent editor settings (see `.editorconfig`)
