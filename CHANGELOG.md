# Changelog

## [0.2.0] - 2026-01-26

### Added
- Dependency building feature with automatic topological ordering
- Dependency tree management system with `DepTree` class
- Program dependency relationships support in build.ezbuild
- Dependency tree tests (287 test cases)
- Missing environment tests (220 new test cases)
- Missing log tests (43 new test cases)
- Example projects for dependency building:
  - Simple dependency with static library (C)
  - Simple dependency with static library (C++)
  - Simple dependency with shared library (C)
  - Simple dependency with shared library (C++)
- Version bump script in utils/version.py
- Project URLs in pyproject.toml (homepage and changelog)

## [0.1.1] - 2026-01-26

### Added
- Language flag to the `init` command for specifying project language
- User prompts when initializing project for better UX

### Fixed
- Wrong if statement in log.py
  - Fixed the test cases for related changes

## [0.1.0] - 2026-01-25

### Added
- Initial CLI implementation with entrypoint
- `init` command for project initialization
- `run` command for executing programs
- `clean` command for cleaning build artifacts
- `compile` command for building programs and libraries
- Environment management system
- Logging utilities
- Filesystem utilities
- Python environment support
- Language enumeration for C/C++
- Support for building C programs
- Support for building C++ programs
- Support for building static libraries (C and C++)
- Support for building shared libraries (C and C++)
- Comprehensive test suite:
  - CLI tests
  - Compile command tests
  - Environment tests
  - Language tests
  - Logging tests
  - Python environment tests
  - Filesystem utility tests
- Example projects:
  - Simple C program
  - Simple C++ program
  - Static library (C)
  - Static library (C++)
  - Shared library (C)
  - Shared library (C++)
- GitHub workflows:
  - Build examples workflow
  - Lint workflow
  - PyPI publish workflow
  - Test workflow
- AGENTS.md with agent development guidelines
- Project configuration files (.editorconfig, .python-version, .gitignore)
